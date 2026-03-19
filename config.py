# config.py

FILE_PATHS = [
    "E:/钢研实习/实习相关文档/新入职实习生流程.docx",
    "E:/钢研实习/实习相关文档/治理平台操作手册2.0.docx",
    "E:/钢研实习/实习相关文档/网宿零信任客户端登录说明.docx"
]

SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.md', '.csv']

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
PERSIST_DIR = "./chroma_db"
SIMILARITY_THRESHOLD = 0.001

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_MODEL = "qwen3-max"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

OPENAI_API_KEY="sk-3b998a250f5b4b48820881504200198e"