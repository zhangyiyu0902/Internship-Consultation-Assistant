# 重要：必须在最开头设置镜像源
import os
import warnings

# 禁用所有警告和日志
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


# 禁用所有日志输出
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("tokenizers").setLevel(logging.ERROR)

from config import FILE_PATHS
from loaders.file_loader import load_all_documents
from processing.text_splitter import split_documents
from vectorstore.chroma_store import load_or_create_vectorstore
from rag.retrieval_chain import create_chain
from rag.qa import ask

warnings.filterwarnings('ignore')

def main():
    docs = load_all_documents(FILE_PATHS)
    if not docs:
        print("没有加载到文档")
        return

    chunks = split_documents(docs)
    vectorstore = load_or_create_vectorstore(chunks)

    chain, retriever = create_chain(vectorstore)

    print("实习入职小助手启动")

    while True:
        q = input("\n问: ").strip()
        if not q:
            continue

        ans = ask(chain, retriever, q)
        print(f"答: {ans}")


if __name__ == "__main__":
    main()