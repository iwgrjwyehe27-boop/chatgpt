# Quick Start Guide for Public Deployment

## Option 1: Replit (Fastest - 2 minutes)

1. Go to **https://replit.com** → Sign up
2. Click **"Create Repl"** → **"Import from GitHub"**
3. Paste: `https://github.com/yourusername/aimode` (or upload ZIP)
4. Click **Secrets 🔒** → Add:
   - `OPENROUTER_API_KEY` = your API key from https://openrouter.ai/keys
   - `OPENROUTER_MODEL` = gpt-4o-mini
5. Click **Run** ▶️
6. **Public URL** appears at top - share it!

---

## Option 2: Render (5 minutes)

1. Go to **https://render.com** → Sign up
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub (or upload ZIP)
4. Fill in:
   - **Name:** `chatbot` (or any name)
   - **Environment:** Python 3
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app`
5. Click **"Advanced"** → Add environment variables:
   - `OPENROUTER_API_KEY` = your API key
   - `OPENROUTER_MODEL` = gpt-4o-mini
6. Click **"Create Web Service"**
7. Wait for deployment, get public URL

---

## Get Your OpenRouter API Key

1. Go to https://openrouter.ai/keys
2. Sign up or login
3. Click **"Create Key"**
4. Copy the key (starts with `sk-or-v1-...`)
5. Use in deployment

---

## That's it! 🎉

Your chatbot is now live on the internet. Share the public URL!

For detailed info, see `DEPLOYMENT.md`
