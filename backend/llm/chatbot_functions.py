#pythainlp
from pythainlp.util import normalize          # สำหรับจัดระเบียบสระ/วรรณยุกต์
from pythainlp.tokenize import word_tokenize  # สำหรับตัดคำ

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from typing import List, Dict

from llm.chatbot_prompts import rewrite_question_prompt_template
from llm.chatbot_llm import get_llm
from llm.embedder import get_embeddings

from database.supabase_client import get_supabase_client

# --- Helper Functions (ฟังก์ชันช่วยทำงาน) ---

def preprocess_thai_text(text: str) -> str:
    """
    ฟังก์ชันทำความสะอาดภาษาไทย (Text Preprocessing) ตาม Proposal
    1. Normalize: แก้ปัญหาสระลอย วรรณยุกต์ซ้อน
    2. Tokenize: ตัดคำและคั่นด้วยช่องว่าง เพื่อให้ Embedding Model จับใจความได้แม่นขึ้น
    """
    # 1. จัดระเบียบตัวอักษร (เช่น สระอำ หรือวรรณยุกต์ที่พิมพ์ผิดลำดับ)
    clean_text = normalize(text)
    
    # 2. ตัดคำแล้วเชื่อมด้วยช่องว่าง (เช่น "ลากิจได้กี่วัน" -> "ลากิจ ได้ กี่ วัน")
    # การทำแบบนี้ช่วยให้โมเดล BGE-M3 เข้าใจขอบเขตคำได้ชัดเจนขึ้น
    words = word_tokenize(clean_text, engine="newmm", keep_whitespace=False)
    
    return " ".join(words)

def retrieve_data(question: str):
    """ฟังก์ชันค้นหากฎหมายจาก Supabase"""
    print(f"    กำลังค้นหาข้อมูลสำหรับ: {question}")
    
    # 1. แปลงคำถามเป็น Vector
    query_vector = get_embeddings(question)
    
    # 2. ยิงไปถาม Supabase (ใช้ฟังก์ชัน match_sections_v2 ที่เราสร้างใน SQL)
    supabase = get_supabase_client()
    response_act = supabase.rpc(
        "match_sections_v2",
        {
            "query_embedding": query_vector,
            "match_threshold": 0.5, # ความเหมือนขั้นต่ำ 50%
            "match_count": 5        # เอามา 5 อันดับแรก
        }
    ).execute()
    response_judg = supabase.rpc(
        "match_judgments_v2",
        {
            "query_embedding": query_vector,
            "match_threshold": 0.5, # ความเหมือนขั้นต่ำ 50%
            "match_count": 1        # เอามา 5 อันดับแรก
        }
    ).execute()
    
    return {
        "sections": response_act.data,
        "judgments": response_judg.data
    }

def get_act_name(act_id: int) -> str:
    """ฟังก์ชันดึงชื่อตรากฎหมายจาก act_id"""
    supabase = get_supabase_client()
    response = supabase.table("acts").select("title").eq("id", act_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]['title']
    return "Unknown Act"

def rewrite_question(question: str, history: List[Dict[str, str]]) -> str:
    """ฟังก์ชัน Context Awareness: แปลงคำถามกว้างๆ ให้ชัดเจนขึ้นโดยดูประวัติ"""
    
    # ถ้าไม่มีประวัติเก่า ก็ใช้คำถามเดิมเลย
    if not history:
        return question
    
    print("    กำลังเรียบเรียงคำถามใหม่ (Query Rewriting)...")
    
    # แปลง History List ให้เป็นข้อความ String
    history_text = ""
    for msg in history[-4:]: # ดูย้อนหลังแค่ 2-3 คู่ล่าสุดพอ (ประหยัด Token)
        role = "User" if msg['role'] == 'user' else "AI"
        history_text += f"{role}: {msg['content']}\n"
    
    # Prompt สั่งให้ AI เขียนคำถามใหม่ (Standalone Question)
    rewrite_template = rewrite_question_prompt_template()
    
    try:
        prompt = PromptTemplate(template=rewrite_template, input_variables=["chat_history", "question"])
        llm = get_llm()  # Lazy load LLM
        chain = prompt | llm | StrOutputParser()
        
        # สั่ง AI ทำงาน
        new_question = chain.invoke({"chat_history": history_text, "question": question})
        
        print(f"    คำถามใหม่ที่ได้: {new_question}")
        return new_question.strip()
        
    except Exception as e:
        print(f"    Error rewriting: {e}")
        return question # ถ้า error ให้ใช้คำถามเดิมไปก่อน