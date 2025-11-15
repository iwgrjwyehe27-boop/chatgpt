#!/usr/bin/env python3
"""
Download a small GGML model for local inference.
Options:
1. Mistral-7B-Instruct-v0.1-gguf (4-bit, ~4 GB) — good quality, slightly larger
2. neural-chat-7b-v3-1 (4-bit, ~3.5 GB) — small, decent quality
3. dolphin-2.0-mistral-7b (4-bit, ~4 GB) — good for RAG

This script downloads option 2 (smallest) by default.
"""
import os
import urllib.request
import argparse


# Model options (examples). To install phi-3 or phi-4-mini, provide a direct download URL
# (GGUF/GGML) from a model repository (Hugging Face or similar). This script accepts
# either a built-in key or a direct URL via --url.
MODELS = {
    'neural-chat-7b': {
        'url': 'https://huggingface.co/TheBloke/neural-chat-7B-v3-1-GGUF/resolve/main/neural-chat-7b-v3-1.Q4_K_M.gguf',
        'size_gb': 3.5,
        'name': 'neural-chat-7b-v3-1.Q4_K_M.gguf'
    },
    'mistral-7b': {
        'url': 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/Mistral-7B-Instruct-v0.1.Q4_K_M.gguf',
        'size_gb': 4.0,
        'name': 'Mistral-7B-Instruct-v0.1.Q4_K_M.gguf'
    },
    'phi-2': {
        'url': 'https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf',
        'size_gb': 1.6,
        'name': 'phi-2.Q4_K_M.gguf'
    }
}


def download_url(url, output_path):
    try:
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) / total_size)
                mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                print(f'\r[{percent:5.1f}%] {mb:6.1f} MB / {total_mb:6.1f} MB', end='', flush=True)

        urllib.request.urlretrieve(url, output_path, reporthook)
        print(f'\n✅ Model downloaded to {output_path}')
        return True
    except Exception as e:
        print(f'\n❌ Download failed: {e}')
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def download_model(model_key=None, url=None, name=None):
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)

    if url:
        # If user provided a URL, use it and infer filename
        filename = name if name else os.path.basename(url.split('?')[0])
        output_path = os.path.join(models_dir, filename)
        if os.path.exists(output_path):
            print(f'Model already exists at {output_path}')
            return True
        print(f'Downloading from URL: {url}')
        return download_url(url, output_path)

    if model_key:
        if model_key not in MODELS:
            print(f'Available models: {", ".join(MODELS.keys())}')
            return False
        info = MODELS[model_key]
        output_path = os.path.join(models_dir, info['name'])
        if os.path.exists(output_path):
            print(f'Model already exists at {output_path}')
            return True
        print(f"Downloading {model_key} ({info.get('size_gb', '?')} GB)...")
        print(f"URL: {info['url']}")
        return download_url(info['url'], output_path)

    print('Either model_key or url must be provided')
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download GGUF/GGML model to models/ folder')
    parser.add_argument('model', nargs='?', help='Known model key (e.g. phi-2, neural-chat-7b) or omit to use --url')
    parser.add_argument('--url', help='Direct URL to model file (GGUF/GGML)')
    parser.add_argument('--name', help='Optional filename to save as')
    args = parser.parse_args()

    # If user passed both a model key and a URL, prefer the URL
    if args.url:
        success = download_model(url=args.url, name=args.name)
    else:
        success = download_model(model_key=args.model)
    exit(0 if success else 1)
