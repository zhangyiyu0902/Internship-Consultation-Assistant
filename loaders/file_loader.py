import os
from pathlib import Path
from config import SUPPORTED_EXTENSIONS

# 建议将通用的 Loader 放在外部，避免循环导入或重复加载
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader

def get_document_loader(file_path):
    # 使用 pathlib 自动处理不同系统的路径分隔符
    path_obj = Path(file_path)
    ext = path_obj.suffix.lower()

    try:
        if ext == '.pdf':
            return PyMuPDFLoader(str(path_obj))
        elif ext in ['.docx', '.doc']:
            return Docx2txtLoader(str(path_obj))
        else:
            # 文本文件增加 utf-8 强制编码，防止 Linux 环境下报错
            return TextLoader(str(path_obj), encoding='utf-8')
    except Exception as e:
        # 打印具体的错误方便在 Streamlit Logs 调试
        print(f"创建 Loader 失败 {file_path}: {e}")
        return TextLoader(str(path_obj), encoding='utf-8')

def scan_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"警告：文件夹不存在 {folder_path}")
        return []

    files = []
    # 统一后缀匹配，支持大小写混写（如 .PDF 和 .pdf）
    for ext in SUPPORTED_EXTENSIONS:
        # rglob 是递归扫描子目录
        files.extend(folder.rglob(f"*{ext.lower()}"))
        files.extend(folder.rglob(f"*{ext.upper()}"))

    return [str(f.absolute()) for f in files]

def load_all_documents(file_paths):
    all_docs = []
    final_paths = []

    # 1. 统一解析所有路径
    for p in file_paths:
        p_obj = Path(p)
        if p_obj.is_dir():
            final_paths.extend(scan_folder(p))
        elif p_obj.is_file():
            final_paths.append(str(p_obj.absolute()))

    # 2. 去重并排序，保证加载顺序一致
    final_paths = sorted(list(set(final_paths)))

    # 3. 循环加载
    for file_path in final_paths:
        try:
            loader = get_document_loader(file_path)
            docs = loader.load()

            for doc in docs:
                # 记录绝对路径和文件名，方便后续溯源
                doc.metadata['source_file'] = file_path
                doc.metadata['file_name'] = os.path.basename(file_path)

            all_docs.extend(docs)
            print(f"✅ 成功加载: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ 加载失败 {file_path}: {e}")
            continue

    return all_docs