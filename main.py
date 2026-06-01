"""
Phonikud TTS API — שרת Hebrew Text-to-Speech
מריץ על Render.com (Free tier)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import soundfile as sf
import numpy as np
import io
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phonikud TTS API", version="1.0.0")

# CORS — מאפשר לאפליקציה PWA לקרוא לשרת
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בפרודקשן — שנה לדומיין שלך
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── טעינת מודלים בהפעלה ──────────────────────────────
phonikud_model = None
piper_model    = None

PHONIKUD_MODEL = os.getenv("PHONIKUD_MODEL", "phonikud-1.0.int8.onnx")
PIPER_MODEL    = os.getenv("PIPER_MODEL",    "model.onnx")
PIPER_CONFIG   = os.getenv("PIPER_CONFIG",   "model.config.json")

@app.on_event("startup")
async def load_models():
    global phonikud_model, piper_model
    try:
        from phonikud_tts import Phonikud, Piper
        logger.info("טוען מודל Phonikud...")
        phonikud_model = Phonikud(PHONIKUD_MODEL)
        logger.info("טוען מודל Piper...")
        piper_model = Piper(PIPER_MODEL, PIPER_CONFIG)
        logger.info("✅ מודלים נטענו בהצלחה")
    except Exception as e:
        logger.error(f"❌ שגיאה בטעינת מודלים: {e}")
        raise


# ── Schema ───────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str           # טקסט עברי (עם ניקוד או בלי)
    format: str = "wav" # wav / mp3


# ── Routes ───────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Phonikud TTS API"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": phonikud_model is not None and piper_model is not None
    }


@app.post("/speak")
async def speak(req: TTSRequest):
    """
    קבל טקסט עברי — החזר אודיו WAV
    
    Body: { "text": "שלום עולם" }
    Response: audio/wav binary
    """
    if not phonikud_model or not piper_model:
        raise HTTPException(status_code=503, detail="מודלים לא נטענו עדיין")

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="טקסט ריק")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="טקסט ארוך מדי (מקסימום 500 תווים)")

    try:
        from phonikud_tts import phonemize

        # שלב 1 — ניקוד + המרה ל-IPA
        phonemes = phonemize(phonikud_model, text)
        logger.info(f"📝 '{text}' → {phonemes}")

        # שלב 2 — סינתזת קול
        audio_data = piper_model.synthesize(phonemes)

        # שלב 3 — המרה ל-WAV
        buffer = io.BytesIO()
        sf.write(buffer, np.array(audio_data), samplerate=22050, format="WAV")
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="audio/wav",
            headers={"Cache-Control": "public, max-age=3600"}
        )

    except Exception as e:
        logger.error(f"❌ שגיאה בסינתזה: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nikud")
async def nikud_only(req: TTSRequest):
    """
    רק ניקוד — מחזיר טקסט מנוקד בלי אודיו
    Body: { "text": "שלום עולם" }
    """
    if not phonikud_model:
        raise HTTPException(status_code=503, detail="מודל לא נטען")

    try:
        from phonikud_tts import phonemize
        phonemes = phonemize(phonikud_model, req.text.strip())
        return {"text": req.text, "phonemes": phonemes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
