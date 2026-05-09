import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
try:
    from database.supabase_client import get_supabase_client
    load_dotenv()
except ModuleNotFoundError:
    # When running this file directly, ensure the project root (backend) is on sys.path
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from database.supabase_client import get_supabase_client
    load_dotenv()
from openai import OpenAI
# Load .env from project root (three levels up from this file)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.opentyphoon.ai/v1"
)
# initialize supabase client
supabase = get_supabase_client()
tags = ["เงินทดแทน", "ทดแทน", "ค่ารักษา", "ค่าฟื้นฟู", 
        "ค่าทำศพ", "อันตราย", "สูญเสีย", "สมรรถภาพ", 
        "กองทุนเงินทดแทน", "นายจ้าง", "ลูกจ้าง", "เงินสมทบ", 
        "กองทุน", "เงิน", "ประกันสังคม", "ผู้ประกันตน", 
        "สิทธิประโยชน์", "ประกัน", "เงินชราภาพ", "รายได้", 
        "การคำนวณ", "ค่าจ้าง", "ความปลอดภัย", "อาชีวอนามัย", 
        "ประเมินอันตราย", "มาตรฐาน", "มาตรการ", "สภาพแวดล้อม", 
        "งาน", "พนักงานตรวจความปลอดภัย", "แผนปฏิบัติการ", 
        "สถาบันส่งเสริม", "กองทุนความปลอดภัย", "พนักงาน", 
        "ประเมิน", "การรายงาน", "การตรวจ", "การติดตาม", 
        "คุ้มครองแรงงาน", "ค่าล่วงเวลา", "วันทำงาน", "วันหยุด", 
        "ค่าชดเชย", "เลิกจ้าง", "จ้างเหมาช่วง", "สวัสดิการ", 
        "แรงงาน", "พนักงานตรวจแรงงาน", "คณะกรรมการค่าจ้าง"]

prompt = f"""วิเคราะห์ชื่อ tag ค่อไปนี้ว่าคำอธิบายควรเป็นอย่างไร โดยอ้างอิงจากกฎหมายแรงงานไทย: {', '.join(tags)}
ตอบในรูปแบบ JSON ที่มี key เป็นชื่อ tag และ value เป็นคำอธิบายสั้น ๆ ของ tag นั้น ๆ
ตัวอย่างรูปแบบการตอบ:
{{
    "เงินทดแทน": "คำอธิบายของเงินทดแทน",
    "ทดแทน": "คำอธิบายของทดแทน",
    ...
}}
"""

messages = [
    {"role": "system", "content": "คุณเป็นโมเดลตีความข้อความภาษาไทย ที่เชี่ยวชาญด้านกฎหมายแรงงานไทย"},
    {"role": "user", "content": prompt}
]

response = client.chat.completions.create(
    model="typhoon-v2.1-12b-instruct",
    messages=messages,
    temperature=0,
    max_tokens=2048
)

tag_descriptions = response.choices[0].message.content
print("Received tag descriptions from OpenAI:", tag_descriptions)
tag_descriptions_dict = json.loads(tag_descriptions[tag_descriptions.index("{"):tag_descriptions.index("}")+1])

for tag, description in tag_descriptions_dict.items():
    supabase.table("tags").insert({
        "name": tag,
        "description": description
    }).execute()
    print(f"Inserted tag: {tag} with description: {description}")