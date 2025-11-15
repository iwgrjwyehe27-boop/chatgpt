# AI Chat Assistant

A modern ChatGPT-style chat interface powered by OpenRouter API. Features real-time chat, image attachments, chat persistence, and a sleek dark theme.

## Features

✨ **Modern UI**
- ChatGPT-inspired dark theme with sidebar
- Smooth animations and transitions
- Responsive design

💬 **Chat Management**
- Create multiple chat sessions
- Rename chats with custom names
- Delete chats with confirmation
- Chat history persists in browser (LocalStorage)
- Auto-sort chats by newest first

🖼️ **Image Support**
- Upload images with messages
- OpenRouter vision model analyzes images
- Images display in chat history

📝 **Message Features**
- Markdown support (bold, headings, line breaks)
- Long responses (up to 2000 tokens)
- Real-time message display

🔐 **Secure**
- API key loaded from environment variables
- Never exposed in browser
- Safe for public deployment

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/aimode
cd aimode

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=gpt-4o-mini
```

```bash
# Run app
python app.py

# Open browser to http://localhost:5000
```

## Deployment

Deploy for free to: [Replit](https://replit.com), [Render](https://render.com), or [PythonAnywhere](https://pythonanywhere.com)

See `QUICK_DEPLOY.md` for step-by-step instructions

## Usage

1. **New Chat** - Click "+ New chat"
2. **Type Message** - Enter text
3. **Add Images** - Click 📎
4. **Send** - Press Enter or click 📤
5. **Manage** - Hover over chat for rename/delete

## Getting OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up (free)
3. Get key from https://openrouter.ai/keys
4. Includes $5 free credits

## Technologies

- **Backend:** Python, Flask
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **AI:** OpenRouter API
- **Storage:** Browser LocalStorage

## Security

✅ API key loaded from environment variables
✅ `.env` file in `.gitignore`
✅ Safe to push to GitHub

## License

MIT - Free to use and modify

🚀 Ready to deploy? See `QUICK_DEPLOY.md`
