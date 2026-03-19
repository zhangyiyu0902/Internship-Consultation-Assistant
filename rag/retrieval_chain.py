from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config import LLM_MODEL, BASE_URL

def create_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.1,
        max_tokens=2000,
        openai_api_base=BASE_URL
    )

    template = """你是公司人力资源部助手，请基于文档以专业且易懂的 HR 语气回答问题。

    约束条件：
    1. 全文仅限一个自然段，严禁换行或空行。
    2. 严禁使用 #、*、-、> 等 Markdown 格式符号。
    3. 必须通过“首先、其次、最后”或“（1）（2）（3）”的方式在文本内部实现分点陈述。
    4. 语言风格要展现 HR 的规范性和亲和力。

    文档内容：
    {context}

    问题：{question}

    回答："""

    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever