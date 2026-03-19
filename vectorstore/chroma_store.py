# vectorstore/chroma_store.py
# -*- coding: utf-8 -*-

import os
import shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import PERSIST_DIR


def get_embedding_model():
    """
    获取中文增强型嵌入模型
    推荐使用 BAAI/bge-small-zh-v1.5 或 shibing624/text2vec-base-chinese
    这些模型在中文语义匹配（如“五险一金”与“社保福利”）上表现极佳
    """
    # 第一次运行会自动下载模型，约 100MB
    model_name = "BAAI/bge-small-zh-v1.5"

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},  # 若有 GPU 可改为 'cuda'
        encode_kwargs={'normalize_embeddings': True}  # 归一化提升余弦相似度准确性
    )


def load_or_create_vectorstore(chunks=None):
    """
    加载或创建向量数据库
    逻辑：
    1. 如果持久化目录存在且没有新片段传入 -> 直接加载本地库 (快)
    2. 如果目录不存在或显式传入了新片段 -> 重新创建并持久化 (准)
    """
    embedding = get_embedding_model()

    # 情况 A：如果本地已经有训练好的“脑子”（索引），且不需要更新数据
    if os.path.exists(PERSIST_DIR) and (chunks is None or len(chunks) == 0):
        print(f"📦 正在从本地加载向量库: {PERSIST_DIR}")
        return Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embedding
        )

    # 情况 B：需要重新构建索引（数据更新了或第一次运行）
    if chunks:
        print(f"🚀 正在构建新的向量库，分块数量: {len(chunks)}")

        # 如果目录已存在但我们需要重建，先清理旧内容防止冲突
        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            persist_directory=PERSIST_DIR
        )
        # 注意：新版 langchain-chroma 在初始化时会自动持久化
        return vectorstore

    else:
        raise ValueError("❌ 错误：既没有本地缓存，也没有传入文档片段，无法初始化向量库。")