import argparse
import pickle
import os
from whoosh import index
from whoosh.qparser import MultifieldParser


PROMPT_TEMPLATE = '''You are a helpful assistant. Use the provided context to answer the user's question. If the answer is not contained in the context, say you don't know.

Context:
{context}

User question: {question}

Answer:'''


def load_index(index_dir, meta_path):
    if not os.path.exists(index_dir):
        raise FileNotFoundError(f'Index directory not found: {index_dir}')
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f'Metadata file not found: {meta_path}')
    ix = index.open_dir(index_dir)
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    return ix, meta


def retrieve(query, ix, top_k=3):
    qp = MultifieldParser(['title', 'content'], schema=ix.schema)
    q = qp.parse(query)
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=top_k)
        contexts = [r['content'] for r in results]
    return contexts


def assemble_prompt(contexts, question):
    context = '\n\n---\n\n'.join(contexts)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def try_run_llama(model_path, prompt, max_tokens=256, temperature=0.2):
    try:
        from llama_cpp import Llama
    except Exception as e:
        print('llama-cpp-python not available or failed to import:', e)
        return None

    print('Using llama-cpp-python with model:', model_path)
    llm = Llama(model_path=model_path)
    resp = llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    if isinstance(resp, dict):
        if 'choices' in resp and len(resp['choices']) > 0:
            return resp['choices'][0].get('text', '')
        return resp.get('output', None)
    return str(resp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', default='models/your-model.ggml', help='Path to GGML model file for llama.cpp/gpt4all')
    parser.add_argument('--index_dir', default='indexdir')
    parser.add_argument('--meta_path', default='metadata.pkl')
    parser.add_argument('--top_k', type=int, default=3)
    parser.add_argument('--max_tokens', type=int, default=256)
    parser.add_argument('--temperature', type=float, default=0.2)
    args = parser.parse_args()

    print('Loading index and metadata...')
    ix, meta = load_index(args.index_dir, args.meta_path)

    print('Ready. Type queries (Ctrl-C to quit).')
    try:
        while True:
            query = input('\nQuestion: ').strip()
            if not query:
                continue
            contexts = retrieve(query, ix, top_k=args.top_k)
            if not contexts:
                print('No relevant documents found.')
                continue
            prompt = assemble_prompt(contexts, query)
            print('\n--- Assembled prompt (first 1000 chars) ---')
            print(prompt[:1000])

            resp = try_run_llama(args.model_path, prompt, max_tokens=args.max_tokens, temperature=args.temperature)
            if resp is None:
                print('\nNo local llama runtime available. Save prompt to prompt.txt or paste into your local model runner.')
                with open('prompt.txt', 'w', encoding='utf-8') as f:
                    f.write(prompt)
                print('Prompt saved to prompt.txt')
            else:
                print('\n--- Model response ---')
                print(resp)

    except KeyboardInterrupt:
        print('\nExiting.')


if __name__ == '__main__':
    main()
