import os
import json
from flask import session, request, jsonify, render_template, url_for
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
import requests
from models import Chat, Message

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'gpt-4o-mini')

print(f"[INIT] OpenRouter initialized with model: {OPENROUTER_MODEL}")

@app.before_request
def make_session_permanent():
    session.permanent = True

def try_run_openrouter(prompt, max_tokens=2000, temperature=0.2, images=None):
    if not OPENROUTER_API_KEY:
        return None, "OpenRouter API key not configured"

    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }

    content = [{'type': 'text', 'text': prompt}]
    if images:
        for img_base64 in images:
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{img_base64}',
                    'detail': 'auto'
                }
            })

    payload = {
        'model': OPENROUTER_MODEL,
        'messages': [{'role': 'user', 'content': content if images else prompt}],
        'max_tokens': max_tokens,
        'temperature': temperature
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        data = resp.json()
        
        if resp.status_code != 200:
            err = data.get('error') if isinstance(data, dict) else None
            return None, f"OpenRouter API error ({resp.status_code}): {err or data}"
        
        choices = data.get('choices') or []
        if len(choices) > 0:
            message = choices[0].get('message') or choices[0]
            text = message.get('content') if isinstance(message, dict) else str(message)
            return (text.strip(), None) if text else (None, None)
        return None, 'No choices in OpenRouter response'
    except Exception as e:
        return None, f"OpenRouter request failed: {e}"

@app.route('/')
def index_route():
    if current_user.is_authenticated:
        return render_template('chat.html', user=current_user)
    return render_template('landing.html')

@app.route('/api/chats', methods=['GET'])
@require_login
def get_chats():
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.updated_at.desc()).all()
    return jsonify({
        'chats': [{
            'id': chat.id,
            'title': chat.title,
            'timestamp': int(chat.updated_at.timestamp() * 1000)
        } for chat in chats]
    })

@app.route('/api/chats', methods=['POST'])
@require_login
def create_chat():
    data = request.json
    chat_id = data.get('id', f'chat_{int(db.func.now().op("*")(1000))}')
    
    chat = Chat(
        id=chat_id,
        user_id=current_user.id,
        title=data.get('title', 'New Chat')
    )
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({'success': True, 'chat_id': chat.id})

@app.route('/api/chats/<chat_id>', methods=['GET'])
@require_login
def get_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    messages = [{
        'text': msg.content,
        'role': msg.role,
        'timestamp': int(msg.created_at.timestamp() * 1000),
        'images': json.loads(msg.images_json) if msg.images_json else []
    } for msg in chat.messages]
    
    return jsonify({
        'chat': {
            'id': chat.id,
            'title': chat.title,
            'messages': messages
        }
    })

@app.route('/api/chats/<chat_id>', methods=['PUT'])
@require_login
def update_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    data = request.json
    if 'title' in data:
        chat.title = data['title']
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
@require_login
def delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/ask', methods=['POST'])
@require_login
def ask():
    data = request.json
    question = data.get('question', '').strip()
    images = data.get('images', [])
    chat_id = data.get('chat_id')
    
    if not chat_id:
        return jsonify({'error': 'Chat ID required'}), 400
    
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    user_message = Message(
        chat_id=chat_id,
        role='user',
        content=question or '[Image message]',
        images_json=json.dumps(images) if images else None
    )
    db.session.add(user_message)
    
    if chat.title == 'New Chat' and question:
        chat.title = question[:30] + ('...' if len(question) > 30 else '')
    
    response, error = try_run_openrouter(question, images=images)
    
    if error:
        db.session.commit()
        return jsonify({'error': error}), 400
    
    assistant_message = Message(
        chat_id=chat_id,
        role='assistant',
        content=response
    )
    db.session.add(assistant_message)
    db.session.commit()
    
    return jsonify({'response': response})
