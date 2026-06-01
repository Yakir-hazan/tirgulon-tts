"""
הורדת מודלים מ-HuggingFace לפני הפעלת השרת
מריץ פעם אחת בעת build על Render
"""

import os
import urllib.request

MODELS = [
    {
        "url": "https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx",
        "filename": "phonikud-1.0.int8.onnx",
    },
    {
        "url": "https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/model.onnx",
        "filename": "model.onnx",
    },
    {
        "url": "https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/model.config.json",
        "filename": "model.config.json",
    },
]

def download():
    for model in MODELS:
        path = model["filename"]
        if os.path.exists(path):
            print(f"✅ כבר קיים: {path}")
            continue
        print(f"⬇️  מוריד {path}...")
        urllib.request.urlretrieve(model["url"], path)
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"✅ הורד: {path} ({size:.1f} MB)")

if __name__ == "__main__":
    download()
