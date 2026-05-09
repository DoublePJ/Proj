import importlib
import os
import glob
import time
from supabase import create_client, Client
from FlagEmbedding import BGEM3FlagModel
from pathlib import Path
from dotenv import load_dotenv
import json
import re
from openai import OpenAI

# Load supabase_client directly to avoid package initialization issues
supabase_client_path = Path(__file__).resolve().parents[2] / "supabase_client.py"
spec = importlib.util.spec_from_file_location("supabase_client", supabase_client_path)
supabase_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supabase_client_module)
_get_supabase_client_direct = supabase_client_module._get_supabase_client_direct

# Load .env from project root
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # fallback to default search

supabase: Client = _get_supabase_client_direct()
print("Supabase client created.")

model = BGEM3FlagModel('BAAI/bge-m3', # model embeddig size 1024
                       use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.opentyphoon.ai/v1"
)
tags = supabase.table("tags").select("id, name").execute().data
tags = {tag['name']: tag['id'] for tag in tags}

thai_to_arabic = str.maketrans("๑๒๓๔๕๖๗๘๙๐","1234567890")

def clean_text(text):
    text = text.translate(thai_to_arabic)
    text = re.sub(r'\s+', ' ', text).replace("*", "").replace("#", "").strip()
    return text

for file in glob.glob("../*/backend/database/input_process/judgments/text/*.txt"):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        judg = f.read()
        judg = judg.splitlines()
    
    print(f"Uploading {judg[0]}...")
    i = 1
    is_detail = False
    judg_summary = ""
    judg_detail = ""
    print(judg)
    while i < len(judg):
        if judg[i].find("ตัดสินเกี่ยวกับปัญหาข้อกฎหมาย") != -1 and not is_detail:
            print(f"Found ตัดสินเกี่ยวกับปัญหาข้อกฎหมาย at line {i}: {judg[i]}")
            print(f"Found คำพิพากษาที่ at line {i}: {"".join(judg[i+2].split(' ')[1:])}")
            print()
            case_number = "".join(judg[i+2].split(' ')[1:])
            is_detail = True
        if judg[i] == '':
            print(f"Found empty line at line {i}, skipping...")
            i+=1
            continue
        if is_detail:
            judg_detail += clean_text(judg[i]) + "\n"
            # print(f"Detail line: {judg_detail}")
        else:
            judg_summary += clean_text(judg[i]) + "\n"
            # print(f"Summary line: {judg_summary}")
        i+=1
    judg_tags = {}
    print(f"Case number: {case_number}")
    print(f"Summary: {judg_summary[:200]}...")  # print only first 200 chars of summary
    print(f"Detail: {judg_detail[:200]}...")  # print only first 200 chars of detail
    try:
        response_judgments = supabase.table("judgments").insert([
            {
                "title": clean_text(judg[0]),
                "case_number": clean_text(case_number),
                "summary": judg_summary,
                "summary_embedding": model.encode(judg_summary, batch_size=1)['dense_vecs'].tolist(),
                "detail": judg_detail,
            },
        ]).execute()
        print(response_judgments.data[0]['id'])
        prompt = f"""
        วิเคราะห์ข้อความต่อไปนี้ว่าเกี่ยวข้องกับ tag ใดบ้างจากรายการด้านล่าง
        ข้อความ: "{judg}"
        tag ที่มี: {", ".join(tags)}
        ตอบในรูปแบบ JSON เท่านั้น เช่น:
        {{"relevant_tags": ["...", "..."]}}
        """
        messages = [
            {"role": "system", "content": "คุณเป็นโมเดลวิเคราะห์ข้อความภาษาไทย ที่เชี่ยวชาญด้านกฎหมายแรงงานไทย"},
            {"role": "user", "content": prompt}
        ]
        response_tags = client.chat.completions.create(
            model="typhoon-v2.5-30b-a3b-instruct",
            messages=messages,
            temperature=0,
            max_tokens=len(prompt) + 1000
        )
        list_tags = response_tags.choices[0].message.content
        relevant_tags = json.loads(list_tags[list_tags.index("{"):list_tags.index("}") + 1]).get("relevant_tags", [])
        print(f"Relevant tags identified: {relevant_tags}")
        for tag_name in relevant_tags:
            tag_id = tags.get(tag_name)
            print(f"Tag name: {tag_name}, Tag ID: {tag_id}")
            if tag_id and tag_name not in judg_tags:
                judg_tags[tag_name] = tag_id
                supabase.table("judgment_tags").insert([
                    {
                        "judgment_id": response_judgments.data[0]['id'],
                        "tag_id": tag_id
                    },
                ]).execute()
    except Exception as exception:
        print("Exception:", str(exception)[:200])  # print only first 200 chars
        time.sleep(180)  # wait longer before retrying