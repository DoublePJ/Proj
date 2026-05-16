# backend/evaluate_rag.py
import os
from dotenv import load_dotenv
load_dotenv()
import time
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import ContextPrecision, ContextRecall, Faithfulness, AnswerRelevancy

# 1. เปลี่ยนมาใช้ ChatOpenAI สำหรับเชื่อมต่อ API ของ Typhoon
from langchain_openai import ChatOpenAI
# อัปเดตการ Import Embedder ตามที่ระบบแจ้งเตือนสีเหลือง
from langchain_huggingface import HuggingFaceEmbeddings 

from llm.chatbot_structure import ChatRequest
from llm.chatbot_service import chat_service
from llm.chatbot_functions import retrieve_data, preprocess_thai_text, rewrite_question
from test_data import TEST_QUESTIONS

# 2. ตั้งค่ากรรมการ (Judge) เป็น Typhoon
# ดึง Key จาก Environment (ต้องมั่นใจว่าในไฟล์ .env มี TYPHOON_API_KEY)
typhoon_judge = ChatOpenAI(
    base_url=os.getenv("TYPHOON_BASE_URL", "https://api.opentyphoon.ai/v1"),
    api_key=os.getenv("TYPHOON_API_KEY"),
    model="typhoon-v2.5-30b-a3b-instruct",
    temperature=0.0,  # บังคับ 0 เพื่อให้การตรวจข้อสอบแม่นยำและมาตรฐานไม่แกว่ง
    max_tokens=4096
)

judge_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

def run_evaluation():
    print(">>> 1. จำลองการถาม-ตอบ เพื่อเตรียมข้อมูลส่งให้ Ragas...")
    data_for_ragas = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for i, item in enumerate(TEST_QUESTIONS):
        user_question = item["question"]
        print(f"[{i+1}/{len(TEST_QUESTIONS)}] กำลังถามบอท: {user_question}")
        
        # ---------------------------------------------------------
        # ใส่บล็อก Debug ไว้ตรงนี้! (ภายในลูป for)
        # ---------------------------------------------------------
        try:
            print("  [Debug] 1. กำลัง preprocess...")
            processed_q = preprocess_thai_text(user_question)
            
            print("  [Debug] 2. กำลังเรียก rewrite_question...")
            search_query = rewrite_question(processed_q, [])
            print(f"  [Debug] --> search_query ได้ชนิดข้อมูล: {type(search_query)}") 
            
            print("  [Debug] 3. กำลังเรียก retrieve_data...")
            retrieved_docs = retrieve_data(search_query)
            print(f"  [Debug] --> retrieved_docs ได้ชนิดข้อมูล: {type(retrieved_docs)}")
            
            # จัดการโครงสร้างข้อมูล Sections
            contexts = []
            if isinstance(retrieved_docs, list):
                contexts = [doc.get('text_original', '') for doc in retrieved_docs if doc.get('text_original')]
            elif isinstance(retrieved_docs, dict):
                contexts = [doc.get('text_original', '') for doc in retrieved_docs.get("sections", []) if doc.get('text_original')]
            
            print("  [Debug] 4. กำลังเรียก chat_service...")
            request = ChatRequest(question=user_question, history=[])
            response = chat_service(request)
            
            # เก็บข้อมูล
            data_for_ragas["question"].append(user_question)
            data_for_ragas["answer"].append(response.answer)
            data_for_ragas["contexts"].append(contexts)
            data_for_ragas["ground_truth"].append(item["ground_truth"])
            
            print("  ✅ สำเร็จ")
        except Exception as e:
            import traceback
            print(f"  ❌ เกิดข้อผิดพลาด: {e}")
            traceback.print_exc() # <--- บรรทัดนี้จะพ่นต้นตอออกมาให้เห็นชัดๆ!
            continue
        # ---------------------------------------------------------
        
        time.sleep(2)

    # ---------------------------------------------------------
    # เช็คว่ามีข้อมูลผ่านเข้ามาบ้างไหมก่อนรัน Ragas
    # ---------------------------------------------------------
    if len(data_for_ragas["question"]) == 0:
        print("\n🚨 ไม่สามารถประเมินผลได้ เนื่องจากทุกข้อเกิด Error หมดเลย!")
        return

    dataset = Dataset.from_dict(data_for_ragas)

    print("\n>>> 2. เริ่มต้นให้คะแนนด้วย Ragas Triad (Typhoon 2.5 Judge)...")
    print("ขั้นตอนนี้อาจใช้เวลาสักพัก...")
    
    # รันการประเมินผล
    result = evaluate(
        dataset=dataset,
        metrics=[ContextPrecision(), ContextRecall(), Faithfulness(), AnswerRelevancy()],
        llm=typhoon_judge,
        embeddings=judge_embeddings,
        raise_exceptions=False # สำคัญ: ป้องกันสคริปต์พังถ้า Typhoon พิมพ์ JSON ผิดฟอร์แมต
    )

    print("\n=== ผลการประเมินคะแนนเฉลี่ย (เต็ม 1.0) ===")
    print(result)
    
    # บันทึกเป็นไฟล์ CSV
    try:
        df = result.to_pandas()
        df.to_csv("ragas_results_qwen.csv", index=False, encoding='utf-8-sig') # เปลี่ยนชื่อไฟล์เป็น Qwen จะได้ไม่ทับของเดิม
        print("\n>>> บันทึกผลลัพธ์รายข้อลงไฟล์ ragas_results_qwen.csv เรียบร้อยแล้ว!")
    except Exception as e:
        print("\n>>> ไม่สามารถบันทึกไฟล์ CSV ได้:", e)

if __name__ == "__main__":
    run_evaluation()