import argparse
import os
import pickle
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import MultifieldParser


def create_schema():
    return Schema(path=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT(stored=True, analyzer=StemmingAnalyzer()))


def index_docs(docs_path, index_dir):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        ix = index.create_in(index_dir, create_schema())
    else:
        ix = index.open_dir(index_dir)

    writer = ix.writer()
    count = 0
    for root, _, files in os.walk(docs_path):
        for fn in sorted(files):
            if not fn.lower().endswith('.txt'):
                continue
            path = os.path.join(root, fn)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                txt = f.read().strip()
            if not txt:
                continue
            writer.update_document(path=path, title=fn, content=txt)
            count += 1
    writer.commit()
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--docs_path', default='docs', help='Folder with .txt docs')
    parser.add_argument('--index_dir', default='indexdir', help='Whoosh index directory')
    parser.add_argument('--meta_path', default='metadata.pkl', help='Output metadata (pickle)')
    args = parser.parse_args()

    print('Loading docs from', args.docs_path)
    if not os.path.exists(args.docs_path):
        print('No documents folder found. Create a docs/ folder and add .txt files.')
        return

    n = index_docs(args.docs_path, args.index_dir)
    print(f'Indexed {n} documents into', args.index_dir)

    # Save a simple metadata list of files
    metas = []
    for root, _, files in os.walk(args.docs_path):
        for fn in sorted(files):
            if fn.lower().endswith('.txt'):
                metas.append({'path': os.path.join(root, fn), 'title': fn})
    with open(args.meta_path, 'wb') as f:
        pickle.dump({'metas': metas}, f)
    print('Metadata saved to', args.meta_path)


if __name__ == '__main__':
    main()
