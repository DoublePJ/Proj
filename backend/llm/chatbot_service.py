import json
# LangChain Imports
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi.responses import StreamingResponse

from llm.chatbot_structure import ChatRequest, ChatResponse
from llm.chatbot_functions import retrieve_data, rewrite_question, preprocess_thai_text, get_act_name
from llm.chatbot_prompts import chat_prompt_template

from llm.chatbot_llm import get_llm

def chat_service(request: ChatRequest) -> ChatResponse:
    """
    ฟังก์ชันหลักของ Chatbot Service
    รับคำถาม + ประวัติการคุย แล้วส่งกลับคำตอบ + แหล่งอ้างอิง
    """
    # --- [NEW] Step 0: Text Preprocessing (PyThaiNLP) ---
    # ตรงตาม Proposal เรื่องการทำความสะอาดและจัดการภาษาธรรมชาติ [cite: 45, 201]
    processed_question = preprocess_thai_text(request.question)
    print(f"    Cleaned Input: {processed_question}") # เช็ค Log ดูว่ามันตัดคำให้ไหม

    # Step 1: Context Awareness (Query Rewriting)
    # เช็คประวัติ แล้วเขียนคำถามใหม่ให้ชัดเจน
    search_query = rewrite_question(request.question, request.history)
    print(f"    Search Query: {search_query}")
    
    # Step 2: Retrieval (ค้นหาข้อมูลจากคำถามใหม่)
    retrieved_docs = retrieve_data(search_query)
    print(f"    Retrieved {len(retrieved_docs)} documents from database.")
    
    # ถ้าหาไม่เจอเลย
    if not retrieved_docs:
        return ChatResponse(answer="ขออภัยครับ ไม่พบข้อมูลกฎหมายที่เกี่ยวข้องกับเรื่องนี้ในฐานข้อมูล", sources=[])

    # Step 3: Prepare Context (เตรียมข้อมูลใส่ Prompt)
    # --- Step 3: Prepare Context (เตรียมข้อมูลใส่ Prompt) ---
    context_text = ""
    sources_set = set() # ใช้ set เพื่อกันซ้ำ
    
    for doc in retrieved_docs:
        sec_num = doc.get('section_number', '?')
        text = doc.get('text_original', '')
        # เก็บเนื้อหาไว้ตอบ (ยังคงเอามาทั้งหมดเพื่อให้ AI อ่าน)
        context_text += f"- มาตรา {sec_num}: {text}\n\n"
        # เก็บเลขมาตราลง set (ถ้ามีอยู่แล้ว มันจะไม่เพิ่มซ้ำ)
        sources_set.add(f"มาตรา {sec_num}")
    # แปลงกลับเป็น list และเรียงลำดับให้สวยงาม (เช่น มาตรา 9, 76, 118)
    # ใช้ lambda เพื่อดึงเลขมาเรียง (ป้องกันการเรียงแบบ string เช่น 1, 10, 2)
    try:
        sources_list = sorted(list(sources_set), key=lambda x: int(x.split()[-1]) if x.split()[-1].isdigit() else 9999)
    except:
        sources_list = sorted(list(sources_set)) # ถ้าเรียงไม่ได้ก็เรียงตามตัวอักษรปกติ
    
    prompt = PromptTemplate(template=chat_prompt_template(), input_variables=["context", "question"])
    llm = get_llm()  # Lazy load LLM
    chain = prompt | llm | StrOutputParser()
    
    # ส่ง search_query (ที่แก้แล้ว) + context ไปให้ AI
    ai_answer = chain.invoke({"context": context_text, "question": search_query})
    
    # Step 5: Return Result (ส่งคำตอบ + แหล่งอ้างอิงกลับไป)
    return ChatResponse(answer=ai_answer, sources=sources_list)

def chat_stream_service(request: ChatRequest) -> StreamingResponse:
    # Step 1: Preprocessing & Rewriting (เหมือนเดิม)
    processed_question = preprocess_thai_text(request.question)
    search_query = rewrite_question(processed_question, request.history)
    print(f"    Search Query: {search_query}")
    
    # Step 2: Retrieval (ค้นหาข้อมูล)
    retrieved_docs = retrieve_data(search_query)
    print(f"    Retrieved {len(retrieved_docs['sections'])}+{len(retrieved_docs['judgments'])} documents from database.")

    # เตรียม Context และ Metadata
    context_text_section = ""
    sections_list = []  # เก็บเลขมาตรา
    acts_set = set()    # เก็บ act_id
    
    # ถ้าหาข้อมูลไม่เจอเลย
    if not retrieved_docs["sections"] and not retrieved_docs["judgments"]:
        async def empty_generator():
            yield json.dumps({
                "type": "error", 
                "message": "ขออภัยครับ ไม่พบข้อมูลกฎหมายที่เกี่ยวข้องกับเรื่องนี้"
            }) + "\n"
        return StreamingResponse(empty_generator(), media_type="application/x-ndjson")

    # จัดการข้อมูลที่เจอ (Context Building)
    for doc in retrieved_docs["sections"]:
        sec_num = doc.get('section_number', '?')
        text = doc.get('text_original', '')
        act_id = doc.get('act_id')
        sec_id = doc.get('id')
        
        # Debug: ดูว่าแต่ละ doc มีอะไรบ้าง
        print(f"    Document: section_number={sec_num}, act_id={act_id}, sec_id={sec_id}")
        
        context_text_section += f"- act_id={act_id} sec_num={sec_num}: {text}\n"
        
        # เก็บเลขมาตราและ act_id
        if sec_num and sec_num != '?':
            sections_list.append({ 
                "id": sec_id, 
                "act_id": act_id, 
                "section_number": sec_num, 
                "paragraph_number": doc.get('paragraph_number')
            })
        if act_id:
            acts_set.add(act_id)
    
    # Debug: ดู metadata ที่เตรียมจะส่ง
    print(f"    Sections collected: {sections_list}")
    print(f"    Acts collected: {list(acts_set)}")
    
    # ดึงชื่อพระราชบัญญัติ
    acts = {}
    for a in acts_set:
        acts[a] = get_act_name(a)
    
    # เตรียม Context และ Metadata
    context_text_judgment = ""
    judgments_list = []
    
    for doc in retrieved_docs["judgments"]:
        judgment_id = doc.get('id')
        judgment_title = doc.get('title', '')
        judgment_case_number = doc.get('case_number', '')
        judgment_summary = doc.get('summary', '')
        
        # Debug: ดูว่าแต่ละ doc มีอะไรบ้าง
        print(f"    Document: judgment_id={judgment_id}, title={judgment_title}, case_number={judgment_case_number}")
        
        context_text_judgment += f"- judgment_id={judgment_id} title={judgment_title} : {judgment_summary}\n"
        
        # เก็บเลขมาตราและ act_id
        if sec_num and sec_num != '?':
            judgments_list.append({ 
                "id": judgment_id, 
                "case_number": judgment_case_number, 
                "title": judgment_title,
                "summary": judgment_summary,
            })
            
    # Debug: ดู metadata ที่เตรียมจะส่ง
    print(f"    Judgments collected: {judgments_list}")
    
    # ดึงชื่อพระราชบัญญัติ
    acts = {}
    for a in acts_set:
        acts[a] = get_act_name(a)
    
    # สร้าง metadata
    metadata = {
        "sections": sorted(sections_list, key=lambda x: x["id"]),
        "judgments": sorted(judgments_list, key=lambda x: x["id"]),
        "acts": sorted(acts.items(), key=lambda x: x[0])  # เรียงตาม act_id
    }
    
    print(f"    Metadata to send: {metadata}")

    # --- Step 3: Generator Function (หัวใจของ Streaming) ---
    async def event_generator():
        # 3.1 ส่ง metadata (sections และ acts) - ไม่ส่ง sources แยกแล้ว
        yield json.dumps({
            "type": "metadata",
            "data": metadata
        }) + "\n"

        prompt = PromptTemplate(template=chat_prompt_template(), input_variables=["context", "question"])
        llm = get_llm()  # Lazy load LLM
        chain = prompt | llm | StrOutputParser()

        # 3.2 สั่ง AI ตอบแบบ Stream (ทีละคำ)
        # ใช้ .astream แทน .invoke เพื่อรับข้อมูลทีละชิ้น
        async for chunk in chain.astream({"context": context_text_section, "question": search_query}):
            # ส่งเนื้อหาทีละนิดไปให้ Frontend
            yield json.dumps({
                "type": "content", 
                "data": chunk
            }) + "\n"

    # ส่งคืนเป็น StreamingResponse
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")