# Lazy-initialized LLM client. Calling get_llm() will create
# and cache the client on first use. This prevents heavy initialization
# at import time, allowing the server to bind to the port quickly.
_llm = None

def get_llm():
    """
    Get or create the LLM client (singleton pattern).
    Initializes on first call, then returns cached instance.
    """
    global _llm
    if _llm is not None:
        return _llm

    # Load environment variables
    import os
    from typing import Optional
    from dotenv import load_dotenv
    load_dotenv()

    print(">>> Initializing LLM client...")
    from langchain_openai import ChatOpenAI
    _llm = ChatOpenAI(
        base_url=os.getenv("TYPHOON_BASE_URL"),  # https://api.opentyphoon.ai/v1
        api_key=os.getenv("TYPHOON_API_KEY"),
        model="typhoon-v2.5-30b-a3b-instruct",   # โมเดลตัวเก่งสุด
        temperature=0.3,                          # ความคิดสร้างสรรค์ต่ำหน่อย เพื่อความแม่นยำทางกฎหมาย
        max_tokens=4096                           # เพิ่มพื้นที่ให้ AI ตอบยาวๆ ได้ ไม่ error
    )
    print(">>> LLM client initialized")
    return _llm