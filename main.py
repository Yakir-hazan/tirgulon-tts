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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

phonikud_model = None
piper_model    = None

PHONIKUD_MODEL = os.getenv("PHONIKUD_MODEL", "phonikud-1.0.int8.onnx")
PIPER_MODEL    = os.getenv("PIPER_MODEL",    "model.onnx")
PIPER_CONFIG   = os.getenv("PIPER_CONFIG",   "model.config.json")

@app.on_event("startup")
async def load_models():
    global phonikud_model, piper_model
    try:
        import sys
        # הוסף את site-packages של venv לpath
        import site
        for sp in site.getsitepackages():
            if sp not in sys.path:
                sys.path.insert(0, sp)

        from phonikud_onnx import Phonikud
        from piper_onnx import Piper

        logger.info("טוען מודל Phonikud...")
        phonikud_model = Phonikud(PHONIKUD_MODEL)
        logger.info("טוען מודל Piper...")
        piper_model = Piper(PIPER_MODEL, PIPER_CONFIG)
        logger.info("✅ מודלים נטענו בהצלחה")
    except Exception as e:
        logger.error(f"❌ שגיאה בטעינת מודלים: {e}")
        raise


class TTSRequest(BaseModel):
    text: str
    format: str = "wav"


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
    if not phonikud_model or not piper_model:
        raise HTTPException(status_code=503, detail="מודלים לא נטענו עדיין")

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="טקסט ריק")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="טקסט ארוך מדי")

    try:
        from phonikud import phonemize as ph_phonemize

        phonemes = ph_phonemize(phonikud_model, text)
        logger.info(f"📝 '{text}' → {phonemes}")

        audio_data = piper_model.synthesize(phonemes)

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
    if not phonikud_model:
        raise HTTPException(status_code=503, detail="מודל לא נטען")

    try:
        from phonikud import phonemize as ph_phonemize
        phonemes = ph_phonemize(phonikud_model, req.text.strip())
        return {"text": req.text, "phonemes": phonemes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))