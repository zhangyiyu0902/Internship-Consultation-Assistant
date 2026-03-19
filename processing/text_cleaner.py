def clean_text(text):
    if not text:
        return text

    import re

    # 去markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s*', '', text)

    # 🔥 关键：把所有换行变成空格
    text = re.sub(r'\s*\n+\s*', ' ', text)

    # 去多余空格
    text = re.sub(r'\s+', ' ', text)

    return text.strip()