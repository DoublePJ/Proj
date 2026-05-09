import os
import glob
import time
import sys
import importlib.util
from supabase import Client
from FlagEmbedding import BGEM3FlagModel
from pathlib import Path
from dotenv import load_dotenv
import json
import re
import ast
from openai import OpenAI

# Load supabase_client directly to avoid package initialization issues
supabase_client_path = Path(__file__).resolve().parents[1] / "supabase_client.py"
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

def get_sturctured_params(text):
    param_str = text.split(";", 1)[0]
    # remove trailing commas before } or ]
    param_str_clean = re.sub(r',\s*(?=[}\]])', '', param_str).strip()
    # Try strict JSON first
    try:
        return json.loads(param_str_clean)
    except json.JSONDecodeError:
        # Fallback to parsing Python literals like single-quoted dicts using ast.literal_eval
        try:
            return ast.literal_eval(param_str_clean)
        except Exception:
            # Try to fix common case where a nested JSON object is embedded as a double-quoted string
            # e.g.  ... "references":{12:"{"text":"..."}}
            # Convert occurrences of :"{...}" into :'{...}' so ast.literal_eval can parse it
            try:
                fixed = re.sub(r':\s*"(\{.*?\})"', r": '\1'", param_str_clean)
                return ast.literal_eval(fixed)
            except Exception:
                # As a last resort, try replacing single quotes with double quotes and parse as JSON
                try:
                    return json.loads(param_str_clean.replace("'", '"'))
                except Exception as e:
                    # Raise a clearer error for debugging
                    raise ValueError(f"Failed to parse params: {param_str_clean}") from e

def text_with_cross_references(text: str, self_params: dict, references: dict[int,dict]) -> str:
    if not references:
        return text
    
    for ref_num, ref_data in sorted(references.items(), key=lambda x: int(x[0]), reverse=True):
        if ref_data.get('book'):
            ref = f"{{\'book\': {ref_data['book']}}}"
        elif ref_data.get('group'):
            ref = f"\'group\': {ref_data['group']}}}"
        elif ref_data.get('super_section'):
            ref = f"\'super_section\': {ref_data['super_section']}}}"
        else:
            ref = f"\'section\': {ref_data['section_number']}" if ref_data.get('section_number') is not None else f"\'section\': {self_params.get('section')}"
            ref += f", \'sub_section\': \'{ref_data['sub_section']}\'" if ref_data.get('sub_section') is not None else ''
            ref += f", \'paragraph\': {ref_data.get('paragraph_number', 1)}"
            ref += f", \'item\': \'{ref_data.get('item', '')}\'" if ref_data.get('item') is not None else ''
        text_cross = next((k for k in act_dict.keys() if k.find(ref) != -1), None)
        referenced_text = act_dict.get(text_cross) if text_cross else None
        if not referenced_text:
            print("*"*20)
            print(f"\'section\': {ref_data['section_number']}," if ref_data.get('section_number') is not None else f"\'section\': {self_params.get('section')}")
            print(f"Processing cross-references for text: {text} with references: {references}")
            print(f"Self params: {self_params}")
            print(f"Found cross-reference key: {text_cross} for ref: {ref}")
            print(f"Referenced text: {referenced_text}")
        if referenced_text:
            text = text.replace(ref_data.get('original_text'), f"\"{referenced_text}\"").replace(r"\n", " ")
    # print(f"Processed text: {text}")
    return text

for file in glob.glob("../*/backend/database/input_process/preprocessv3/preprocess_*.txt"):
    print(file)
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        act = f.read()
        act = act.splitlines()
    
    print(f"Uploading {file}...")
    preface = ''
    i=1
    while get_sturctured_params(act[i]).get("intro") == True:
        preface += act[i].split(";", 1)[1] + "\n"
        i += 1
    response_act = None
    try:
        response_act = (
            supabase.table("acts")
            .insert([
                {"title": file[file.find("preprocess_") + len("preprocess_"):file.find(".txt")], "preface": preface}
            ])
            .execute()
        )
        print("Response:", response_act)
    except Exception as exception:
        print("Exception:", exception)

    # If act insertion failed, skip inserting its sections to avoid NameError
    if not response_act or not getattr(response_act, "data", None) or not response_act.data:
        print(f"Skipping sections for {file} because act insertion failed.")
        continue
    
    response_act_books = supabase.table("act_books").insert([
        {"act_id": response_act.data[0]['id'], "book_number": 0, "book_title": "บรรพเริ่มต้น"}
    ]).execute()
    response_act_groups = supabase.table("act_groups").insert([
        {"act_id": response_act.data[0]['id'], "book_id": response_act_books.data[0]['id'], "group_number": 0, "group_title": "ลักษณะเริ่มต้น"}
    ]).execute()
    response_act_super_sections = supabase.table("act_super_sections").insert([
        {"act_id": response_act.data[0]['id'], "group_id": response_act_groups.data[0]['id'], "super_number": 0, "super_title": "หมวดเริ่มต้น"}
    ]).execute()
    act_dict = {}
    for line in act[i:]:
        params, text = line.split(";", 1)
        params_dict = get_sturctured_params(line)
        act_dict[str(params_dict)] = text
    act_tags = {}
    while i < len(act):
        line = act[i]
        params, text = line.split(";", 1)
        params_dict = get_sturctured_params(line)
        print(f"Inserting {params_dict}...")
        try:
            if params_dict.get("paragraph"):
                if params_dict.get("references"):
                    text_processed = text_with_cross_references(text, params_dict, params_dict.get("references"))
                else:
                    text_processed = text
                if (params_dict.get("group") == 0) and \
                    (0 != response_act_groups.data[0]["group_number"]):
                        response_act_groups = supabase.table("act_groups").insert([
                            {
                                "act_id": response_act.data[0]['id'],
                                "book_id": response_act_books.data[0]['id'],
                                "group_number": 0,
                                "group_title": "ลักษณะเริ่มต้น"
                            },
                        ]).execute()
                if (params_dict.get("super_section") == 0) and \
                    (0 != response_act_super_sections.data[0]["super_number"]):
                        response_act_super_sections = supabase.table("act_super_sections").insert([
                            {
                                "act_id": response_act.data[0]['id'],
                                "group_id": response_act_groups.data[0]['id'],
                                "super_number": 0,
                                "super_title": "หมวดเริ่มต้น"
                            },
                        ]).execute()
                response_act_sections = supabase.table("act_sections").insert([
                    {
                        "act_id": response_act.data[0]['id'],
                        "book_id": response_act_books.data[0]['id'],
                        "group_id": response_act_groups.data[0]['id'],
                        "super_id": response_act_super_sections.data[0]['id'],
                        "section_number": params_dict.get("section"),
                        "sub_section": params_dict.get("sub_section"),
                        "paragraph_number": params_dict.get("paragraph"),
                        "item_order": params_dict.get("item"),
                        "text_original": text,
                        "text_processed": text_processed,
                        "embedding": model.encode(text_processed, batch_size=1)['dense_vecs'].tolist(),
                        "cross_references": params_dict.get("references", {}),
                        "external_citations": params_dict.get("citation", {}),
                    },
                ]).execute()
                prompt = f"""
                วิเคราะห์ข้อความต่อไปนี้ว่าเกี่ยวข้องกับ tag ใดบ้างจากรายการด้านล่าง
                ข้อความ: "{text_processed}"
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
                for tag_name in relevant_tags:
                    tag_id = tags.get(tag_name)
                    print(f"Tag name: {tag_name}, Tag ID: {tag_id}")
                    if tag_id:
                        act_tags[tag_name] = tag_id
                        supabase.table("act_section_tags").insert([
                            {
                                "act_section_id": response_act_sections.data[0]['id'],
                                "tag_id": tag_id
                            },
                        ]).execute()
            elif params_dict.get("super_section"):
                response_act_super_sections = supabase.table("act_super_sections").insert([
                    {
                        "act_id": response_act.data[0]['id'],
                        "group_id": response_act_groups.data[0]['id'],
                        "super_number": params_dict.get("super_section"),
                        "super_title": text
                    },
                ]).execute()
            elif params_dict.get("group"):
                response_act_super_sections.data[0]["super_number"] = None
                response_act_groups = supabase.table("act_groups").insert([
                    {
                        "act_id": response_act.data[0]['id'],
                        "book_id": response_act_books.data[0]['id'],
                        "group_number": params_dict.get("group"),
                        "group_title": text
                    },
                ]).execute()
            elif params_dict.get("book"):
                response_act_groups.data[0]["group_number"] = None
                response_act_super_sections.data[0]["super_number"] = None
                response_act_books = supabase.table("act_books").insert([
                    {
                        "act_id": response_act.data[0]['id'],
                        "book_number": params_dict.get("book"),
                        "book_title": text
                    },
                ]).execute()
            elif params_dict.get("citation"):
                response_citation = supabase.table("citations").insert([
                    {
                        "act_id": response_act.data[0]['id'],
                        "reference_number": params_dict.get("citation"),
                        "citation_text": text,
                    },
                ]).execute()
            else:
                print(f"Unknown params: {params_dict}")
        except Exception as exception:
            print("Exception:", str(exception)[:200])  # print only first 200 chars
            if "'code': 520," in str(exception):
                print("Rate limit exceeded. Waiting for 3 minutes before retrying...")
                i-=1  # retry this line
                time.sleep(180)  # wait longer before retrying
            print("Text:", text)
            print("Params:", params_dict)
        i+=1
    print(f"Finished inserting sections for {file}. Now linking act tags...")
    print(f"Act tags to link: {act_tags}")
    time.sleep(45)
    for tag_name, tag_id in act_tags.items():
        supabase.table("act_tags").insert([
            {
                "act_id": response_act.data[0]['id'],
                "tag_id": tag_id
            },
        ]).execute()
    print(f"Finished uploading {file}. sleeping for 60 seconds...")
    time.sleep(60)  # brief pause between files to avoid overwhelming the database