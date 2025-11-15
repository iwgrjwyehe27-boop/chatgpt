# AI Chat Assistant

## Overview
A modern ChatGPT-style AI chat assistant imported from GitHub. This Flask-based web application provides a beautiful dark theme interface for chatting with AI models through the OpenRouter API.

## Purpose
- Provide an interactive AI chat interface similar to ChatGPT
- Support multiple chat sessions with persistence
- Enable image uploads for vision-based AI analysis
- Offer a user-friendly experience with modern UI design

## Current State
✅ **Fully Functional** - The application is successfully running on Replit with:
- Flask backend configured for port 5000
- OpenRouter API integration (using gpt-4o-mini model)
- Dark theme UI matching ChatGPT design
- Chat persistence via browser LocalStorage
- Image upload support for vision models

## Recent Changes (November 15, 2025)
- Imported project from GitHub repository: https://github.com/iwgrjwyehe27-boop/chatgpt
- Fixed Werkzeug version conflict in requirements.txt (changed from ==2.3.0 to >=2.3.3)
- Updated Flask app.py to bind to 0.0.0.0:5000 for Replit compatibility
- Installed Python 3.11 and all project dependencies
- Configured OpenRouter API key via Replit Secrets
- Set up workflow to run Flask application on port 5000
- **Added comprehensive responsive design for all devices:**
  - Mobile menu (hamburger button) to access sidebar on phones/tablets
  - Multiple breakpoints: Desktop (>900px), Tablet (600-900px), Mobile (400-600px), Small mobile (<400px)
  - Optimized message bubbles, text sizes, and buttons for each device
  - Device detection functionality
  - Sidebar slides in/out with smooth animations on mobile
  - All features accessible on all screen sizes (no information loss)
  - Touch-friendly button sizes for mobile devices

## Project Architecture

### Backend (Python/Flask)
- **app.py** - Main Flask application with API endpoints
  - `/` - Main chat interface
  - `/api/ask` - Handle chat messages and return AI responses
  - `/api/models/select` - Change AI model
  - `/api/models/force-load` - Test OpenRouter API connection
- **OpenRouter Integration** - Uses OpenRouter API for AI inference with support for multiple models and vision capabilities

### Frontend
- **templates/** - HTML templates for the chat interface
- **Modern UI Features:**
  - Dark theme with ChatGPT-inspired design
  - Sidebar for chat management
  - Real-time message display
  - Markdown support in responses
  - Image attachment support

### Dependencies
- Flask 2.3.2 - Web framework
- Werkzeug >=2.3.3 - WSGI utilities
- requests 2.31.0 - HTTP library for API calls
- Whoosh 2.7.4 - Full-text search library
- python-dotenv 1.0.0 - Environment variable management
- gunicorn 21.2.0 - Production WSGI server

### Environment Variables
- `OPENROUTER_API_KEY` - API key for OpenRouter service (configured via Replit Secrets)
- `OPENROUTER_MODEL` - AI model to use (defaults to gpt-4o-mini)
- `PORT` - Server port (defaults to 5000)

## Key Features
1. **Multiple Chat Sessions** - Create, rename, and delete chat conversations
2. **Image Support** - Upload images for AI vision model analysis
3. **Chat Persistence** - Conversations saved in browser LocalStorage
4. **Markdown Rendering** - Rich text formatting in AI responses
5. **Model Selection** - Choose different AI models via API
6. **Secure API Management** - API keys stored safely in environment variables

## Usage
The application is ready to use:
1. Click "+ New chat" to start a conversation
2. Type messages in the input box
3. Click the attachment icon (📎) to upload images
4. Send messages by pressing Enter or clicking the send button
5. Manage chats by hovering over them in the sidebar

## Technical Notes
- Binds to 0.0.0.0:5000 for proper Replit proxy compatibility
- Uses OpenRouter API for AI model access
- Chat data stored client-side in browser LocalStorage
- Supports vision models for image analysis
- Production deployment ready with gunicorn

## User Preferences
None specified yet.
