import os
from pathlib import Path
from config import SUPPORTED_EXTENSIONS

def get_document_loader(file_path):
    ext = Path(file_path).suffix.lower()

    try:
        if ext == '.pdf':
            from langchain_community.document_loaders import PyMuPDFLoader
            return PyMuPDFLoader(file_path)
        elif ext in ['.docx', '.doc']:
            from langchain_community.document_loaders import Docx2txtLoader
            return Docx2txtLoader(file_path)
        else:
            from langchain_community.document_loaders import TextLoader
            return TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
    except:
        from langchain_community.document_loaders import TextLoader
        return TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)


def scan_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        return []

    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(folder.rglob(f"*{ext}"))

    return [str(f) for f in files]


def load_all_documents(file_paths):
    all_docs = []
    paths = []

    for p in file_paths:
        if os.path.isdir(p):
            paths.extend(scan_folder(p))
        else:
            paths.append(p)

    paths = list(set(paths))

    for file_path in paths:
        try:
            loader = get_document_loader(file_path)
            docs = loader.load()

            for doc in docs:
                doc.metadata['source_file'] = file_path
                doc.metadata['file_name'] = os.path.basename(file_path)

            all_docs.extend(docs)
        except:
            pass

    return all_docs