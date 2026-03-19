from processing.text_cleaner import clean_text

def ask(chain, retriever, question, threshold=0.1):
    """
    问答函数：
    - chain: RAG问答链
    - retriever: 检索器
    - question: 用户问题
    - threshold: 相似度阈值，低于这个返回“不知道”
    """
    # 相似文档检索
    docs_with_scores = retriever.vectorstore.similarity_search_with_score(question, k=5)

    if not docs_with_scores:
        return "不知道", []

    # 用最高相似度文档判断
    top_score = 1 / (1 + docs_with_scores[0][1])
    if top_score < threshold:
        return "不知道", docs_with_scores

    # 生成回答
    answer = chain.invoke(question)
    answer = clean_text(answer)

    # 再保险一次去掉换行
    answer = answer.replace("\n", " ").strip()

    # 检查空回答
    if not answer:
        return "不知道", docs_with_scores

    return answer, docs_with_scores