# app.py
# -*- coding: utf-8 -*-

import streamlit as st
import time
import datetime
from config import FILE_PATHS, SIMILARITY_THRESHOLD
from loaders.file_loader import load_all_documents
from processing.text_splitter import split_documents
from vectorstore.chroma_store import load_or_create_vectorstore
from rag.retrieval_chain import create_chain
from rag.qa import ask
import os

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
# ================== 页面配置 ==================
st.set_page_config(
    page_title="实习生智能助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认收起侧边栏
)

# ================== 核心 CSS 样式 ==================
st.markdown("""
<style>
    /* 1. 彻底隐藏侧边栏及其控制按钮 */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none;
    }

    /* 2. 全局基础背景与文字 */
    .stApp {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        color: black !important;
    }

    /* 3. 限制主内容宽度，防止宽屏模式下文字太散 */
    .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
    }

    /* 4. 聊天气泡样式 */
    .chat-bubble {
        padding: 14px 18px;
        border-radius: 18px;
        margin-bottom: 4px;
        line-height: 1.6;
        font-size: 1rem;
        max-width: 85%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        display: inline-block;
    }
    .assistant-bubble {
        background-color: #ffffff !important;
        color: black !important;
        border: 1px solid #e5e7eb;
        border-bottom-left-radius: 4px;
    }
    .user-bubble {
        background: white !important;
        color: black !important;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        float: right;
        clear: both;
    }
    .timestamp {
        font-size: 0.75rem;
        color:black;
        opacity: 0.6;
        margin-top: 5px;
        display: block;
        color: #6b7280;
    }

    /* 5. 状态框 (思考中) 样式修复 */
    [data-testid="stStatusWidget"] {
        margin-bottom: -10px !important;
        border: 1px solid #e5e7eb !important;
        background-color: white !important;
    }
    [data-testid="stStatusWidget"] * {
        color: black !important;
    }

    /* 6. 标题美化 */
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #4f46e5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }

    header, .stDeployButton { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ================== 辅助函数 ==================

@st.cache_resource(show_spinner=False)
def init_system():
    try:
        documents = load_all_documents(FILE_PATHS)
        chunks = split_documents(documents)
        vectorstore = load_or_create_vectorstore(chunks)
        chain, retriever = create_chain(vectorstore)
        return chain, retriever
    except Exception as e:
        st.error(f"❌ 系统加载失败: {str(e)}")
        return None, None


def get_time():
    return datetime.datetime.now().strftime("%H:%M")


def stream_display(text):
    placeholder = st.empty()
    full_response = ""
    for char in text:
        full_response += char
        placeholder.markdown(f'<div class="chat-bubble assistant-bubble">{full_response}▌</div>',
                             unsafe_allow_html=True)
        time.sleep(0.01)
    placeholder.markdown(
        f'<div class="chat-bubble assistant-bubble">{full_response}<span class="timestamp">{get_time()}</span></div>',
        unsafe_allow_html=True)


# ================== 主界面内容 ==================
st.markdown('<h1 class="hero-title">🎓 实习生入职小助手</h1>', unsafe_allow_html=True)

chain, retriever = init_system()

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 同学你好！我是你的入职管家。你想了解关于入职、考勤或福利的哪些信息？",
        "time": get_time()
    }]

# 渲染历史
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div style="width:100%; overflow:auto;"><div class="chat-bubble user-bubble">{msg["content"]}<span class="timestamp">{msg["time"]}</span></div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="chat-bubble assistant-bubble">{msg["content"]}<span class="timestamp">{msg["time"]}</span></div>',
            unsafe_allow_html=True)

# ================== 输入处理 ==================
user_input = st.chat_input("输入您的问题，例如：入职材料有哪些？")

if user_input:
    # 1. 渲染用户问题
    st.markdown(
        f'<div style="width:100%; overflow:auto;"><div class="chat-bubble user-bubble">{user_input}<span class="timestamp">{get_time()}</span></div></div>',
        unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input, "time": get_time()})

    # 2. AI 思考与回答
    with st.chat_message("assistant", avatar="🎓"):
        with st.status("🚀 正在查阅文档并思考...", expanded=True) as status:
            try:
                ans, docs = ask(chain, retriever, user_input, SIMILARITY_THRESHOLD)
                status.update(label="✅ 检索完成", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ 连接错误", state="error")
                ans, docs = f"抱歉，系统暂时无法响应：{str(e)}", []

        if ans:
            stream_display(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans, "time": get_time()})

# 底部留白
st.write("")