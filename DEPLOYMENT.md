# Deployment Guide

## Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file from template:**
```bash
cp .env.example .env
```

3. **Edit `.env` with your OpenRouter API key:**
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=gpt-4o-mini
```

4. **Run locally:**
```bash
python app.py
```

Visit `http://localhost:5000`

---

## Deploy to Replit (Recommended - Easiest)

1. **Go to replit.com and sign up**

2. **Create a new Repl:**
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Paste your repo URL (or upload ZIP)

3. **Add environment variables:**
   - Click the 🔒 "Secrets" button (left sidebar)
   - Add these secrets:
     - `OPENROUTER_API_KEY` = your API key
     - `OPENROUTER_MODEL` = gpt-4o-mini

4. **Click "Run"** - your app will start automatically
   - Public URL appears at the top

---

## Deploy to Render

1. **Push code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Go to render.com and sign up**

3. **Create a new Web Service:**
   - Connect GitHub repo
   - Name: "chatbot"
   - Environment: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`

4. **Add environment variables:**
   - Go to Environment tab
   - Add `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`

5. **Deploy** - automatic deployment happens

---

## Deploy to PythonAnywhere

1. **Go to pythonanywhere.com and sign up**

2. **Upload files:**
   - Use Web tab → Upload files
   - Or use Git clone

3. **Create Web app:**
   - Web tab → Add new web app
   - Python 3.9
   - Flask
   - Point to `app.py`

4. **Install dependencies:**
   - Bash console
   - `pip install -r requirements.txt`

5. **Set environment variables:**
   - Web app settings
   - Environment variables section
   - Add `OPENROUTER_API_KEY`

6. **Reload web app** - done!

---

## Security Checklist

✅ Never commit `.env` file (it's in `.gitignore`)
✅ Use environment variables for all secrets
✅ `.env.example` shows template without real keys
✅ API key is loaded from environment, never hardcoded
✅ Safe to push to GitHub public repo

---

## Troubleshooting

**"API key not found" error:**
- Make sure environment variable is set correctly
- Variable name must be exactly `OPENROUTER_API_KEY`
- Restart app after changing variables

**"Module not found" error:**
- Run `pip install -r requirements.txt`
- Or upload `requirements.txt` to your hosting platform

**App not starting:**
- Check Flask is running on `0.0.0.0:5000`
- Check all dependencies in `requirements.txt`
