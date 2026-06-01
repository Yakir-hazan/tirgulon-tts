# Phonikud TTS API 🎙️

שרת Hebrew Text-to-Speech לאפליקציית תרגולון.  
מבוסס על [Phonikud](https://github.com/thewh1teagle/phonikud) + Piper.

---

## פריסה על Render — צעד אחר צעד

### שלב 1 — העלה ל-GitHub
```bash
git init
git add .
git commit -m "phonikud tts api"
git remote add origin https://github.com/YOUR_USERNAME/phonikud-api.git
git push -u origin main
```

### שלב 2 — צור Web Service על Render
1. נכנס ל-render.com
2. לחץ **New → Web Service**
3. חבר את ה-GitHub repo
4. הגדרות:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python download_models.py`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### שלב 3 — עדכן tts.js
```javascript
// שנה את השורה הזו ב-tts.js:
const TTS_API_URL = 'https://YOUR-SERVICE-NAME.onrender.com';
```

### שלב 4 — הוסף tts.js לאפליקציה
```html
<!-- ב-index.html לפני app.js -->
<script src="tts.js"></script>
```

---

## API Endpoints

### POST /speak
מקבל טקסט — מחזיר WAV
```json
{ "text": "שלום עולם" }
```

### POST /nikud  
מקבל טקסט — מחזיר פונמות בלבד (ללא אודיו)
```json
{ "text": "שלום עולם" }
```

### GET /health
בדיקת תקינות השרת

---

## הערות חשובות

- **Free tier על Render:** השרת נרדם אחרי 15 דקות. `warmUpTTS()` ב-tts.js מעיר אותו אוטומטית.
- **Cache:** האפליקציה שומרת מילים שכבר הושמעו בזיכרון — לא קורא לשרת פעמיים.
- **Fallback:** אם השרת לא זמין, חוזר אוטומטית ל-Web Speech API.
