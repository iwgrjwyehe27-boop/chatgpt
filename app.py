#!/usr/bin/env python3
"""
Flask web UI for the OpenRouter-powered AI assistant.
Access at http://localhost:5000
"""
import os
import pickle
from flask import Flask, render_template, request, jsonify, redirect
from whoosh import index
from whoosh.qparser import MultifieldParser
import requests

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

app = Flask(__name__)

PROMPT_TEMPLATE = '''You are a helpful assistant. Use the provided context to answer the user's question. If the answer is not contained in the context, say you don't know.

Context:
{context}

User question: {question}

Answer:'''

INDEX_DIR = 'indexdir'
META_PATH = 'metadata.pkl'

# OpenRouter configuration (required)
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    SETTINGS_FILE = 'aimode_settings.txt'
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('openrouter_api_key='):
                        OPENROUTER_API_KEY = line.split('=', 1)[1]
                    elif line.startswith('openrouter_model='):
                        # allow overriding default model via settings file
                        OPENROUTER_MODEL = line.split('=', 1)[1]
        except Exception:
            pass

# Default OpenRouter model (can be overridden in settings)
OPENROUTER_MODEL = globals().get('OPENROUTER_MODEL', 'gpt-4o-mini')

if not OPENROUTER_API_KEY:
    raise ValueError(
        "[INIT ERROR] OpenRouter API key not found. Please set OPENROUTER_API_KEY env var or add 'openrouter_api_key=...' to aimode_settings.txt"
    )

print(f"[INIT] OpenRouter initialized with model: {OPENROUTER_MODEL}")


def try_run_openrouter(prompt,
                       max_tokens=2000,
                       temperature=0.2,
                       images=None,
                       model=None):
    """Call OpenRouter API for inference using a standard chat completions call.
    Supports multimodal content with images.
    Returns (text, None) on success or (None, error_message) on failure.

    Args:
        prompt: Text content of the message
        max_tokens: Maximum tokens in response
        temperature: Temperature for response generation
        images: List of base64-encoded images (optional)
        model: Model to use (optional, defaults to OPENROUTER_MODEL)
    """
    if not OPENROUTER_API_KEY:
        return None, "OpenRouter API key not configured. Set OPENROUTER_API_KEY or add 'openrouter_api_key=...' to aimode_settings.txt"

    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Use provided model or default to OPENROUTER_MODEL
    model_to_use = model or OPENROUTER_MODEL

    # Build message content with text and optional images
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
        'model': model_to_use,
        'messages': [{
            'role': 'user',
            'content': content if images else prompt
        }],
        'max_tokens': max_tokens,
        'temperature': temperature
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        return None, f"OpenRouter request failed: {e}"

    try:
        data = resp.json()
    except Exception:
        return None, f"OpenRouter returned non-JSON response: {resp.text}"

    if resp.status_code != 200:
        # Return the error detail if present
        err = data.get('error') if isinstance(data, dict) else None
        return None, f"OpenRouter API error ({resp.status_code}): {err or data}"

    try:
        # Standard OpenAI-like response parsing
        choices = data.get('choices') or []
        if len(choices) > 0:
            # choice may contain message.content
            message = choices[0].get('message') or choices[0]
            text = message.get('content') if isinstance(message,
                                                        dict) else str(message)
            return (text.strip(), None) if text else (None, None)
        return None, 'No choices in OpenRouter response'
    except Exception as e:
        return None, f"Error parsing OpenRouter response: {e}"


# Global index and metadata cache
ix = None
meta = None


def load_index_and_meta():
    global ix, meta
    if ix is None:
        if not os.path.exists(INDEX_DIR):
            raise FileNotFoundError(f'Index directory not found: {INDEX_DIR}')
        ix = index.open_dir(INDEX_DIR)
    if meta is None:
        if os.path.exists(META_PATH):
            with open(META_PATH, 'rb') as f:
                meta = pickle.load(f)
        else:
            meta = {'metas': []}
    return ix, meta


def retrieve(query, top_k=3):
    ix, meta = load_index_and_meta()
    qp = MultifieldParser(['title', 'content'], schema=ix.schema)
    q = qp.parse(query)
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=top_k)
        contexts = [r['content'] for r in results]
    return contexts


def assemble_prompt(contexts, question):
    if not contexts:
        return "No documents found for your query."
    context = '\n\n---\n\n'.join(contexts)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def try_run_groq(prompt, max_tokens=64, temperature=0.2):
    """DEPRECATED: This function is no longer used. Use try_run_openrouter() instead."""
    return None, "Groq API is not configured. Please use OpenRouter instead."


@app.route('/')
def index_route():
    return render_template('index.html')


@app.route('/authorize', methods=['GET'])
def authorize():
    """Compatibility route: some clients may try to call /authorize for OAuth-like flows.
    This local app doesn't require authentication, so return a friendly message and
    redirect to the main page.
    """
    # For browsers and clients, issue an HTTP redirect to the UI root
    return redirect('/')


@app.route('/api/ask', methods=['POST'])
def ask():
    global OPENROUTER_MODEL

    data = request.json
    question = data.get('question', '').strip()
    images = data.get('images', [])  # List of base64-encoded images
    selected_model = data.get(
        'model',
        OPENROUTER_MODEL)  # Get model from request, default to current

    if not question:
        return jsonify({'error': 'Question cannot be empty'}), 400

    try:
        print(f"[/api/ask] Received question: {question[:100]}...")
        if images:
            print(f"[/api/ask] Received {len(images)} image(s)")
        print(f"[/api/ask] Using model: {selected_model}")

        # Call OpenRouter with the selected model
        print(f"[/api/ask] Calling try_run_openrouter()...")
        response, error = try_run_openrouter(question,
                                             images=images if images else None,
                                             model=selected_model)
        print(
            f"[/api/ask] try_run_openrouter returned: error={error}, response_type={type(response)}, response_len={len(str(response)) if response else 0}"
        )

        if error:
            print(f"[/api/ask] Returning error response: {error}")
            return jsonify({
                'response': None,
                'error': error,
                'ai_backend': 'openrouter'
            }), 200

        print(
            f"[/api/ask] Returning success response with {len(str(response)) if response else 0} chars"
        )
        return jsonify({
            'response': response,
            'error': None,
            'ai_backend': 'openrouter'
        }), 200
    except Exception as e:
        import traceback
        print(f"[/api/ask] Exception: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    try:
        load_index_and_meta()
        return jsonify({
            'index_loaded': True,
            'ai_backend': 'OpenRouter',
            'model': OPENROUTER_MODEL,
            'api_key_set': bool(OPENROUTER_API_KEY)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/list', methods=['GET'])
def list_models():
    """Return a list of available Groq models."""
    # Available Groq models (verified working)
    groq_models = [
        {
            'name': 'llama2-70b-4096',
            'provider': 'Groq',
            'size': '70B',
            'context': 4096
        },
        {
            'name': 'gemma-7b-it',
            'provider': 'Groq',
            'size': '7B',
            'context': 8192
        },
    ]
    return jsonify({'models': groq_models}), 200


@app.route('/api/models/select', methods=['POST'])
def select_model():
    """Select an OpenRouter model."""
    global OPENROUTER_MODEL

    data = request.json
    model_name = data.get('model_name')

    if model_name:
        OPENROUTER_MODEL = model_name
        print(
            f"[/api/models/select] Switched to OpenRouter model: {OPENROUTER_MODEL}"
        )

    return jsonify({
        'current_model': OPENROUTER_MODEL,
        'message': 'Model updated'
    }), 200


@app.route('/api/models/force-load', methods=['POST'])
def force_load_model():
    """Test the OpenRouter API key and selected model."""
    try:
        print(
            f"[/api/models/force-load] Testing OpenRouter API with model: {OPENROUTER_MODEL}"
        )
        response, error = try_run_openrouter("Hello, test.",
                                             max_tokens=10,
                                             temperature=0.2)

        if error:
            return jsonify({
                'success': False,
                'error': error,
                'message': 'OpenRouter API test failed'
            }), 400

        return jsonify({
            'success': True,
            'message':
            f'OpenRouter API is working. Using model: {OPENROUTER_MODEL}',
            'model': OPENROUTER_MODEL
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'OpenRouter API test failed'
        }), 400


if __name__ == '__main__':
    print('Starting Local CPU Assistant Web UI...')
    print('Visit http://localhost:5000 in your browser')

    # Allow PORT to be set by hosting provider
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if os.environ.get(
        'ENVIRONMENT') == 'production' else '127.0.0.1'

    app.run(debug=False, host=host, port=port)
