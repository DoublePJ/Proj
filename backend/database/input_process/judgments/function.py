import os
from openai import OpenAI
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # fallback to default search

def extract_text(file_path, model="typhoon-ocr", task_type="default", max_tokens=16000, temperature=0.1, top_p=0.6, repetition_penalty=1.1, pages=None):
    url = "https://api.opentyphoon.ai/v1/ocr"

    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {
            'model': model,
            'task_type': task_type,
            'max_tokens': str(max_tokens),
            'temperature': str(temperature),
            'top_p': str(top_p),
            'repetition_penalty': str(repetition_penalty)
        }

        if pages:
            data['pages'] = json.dumps(pages)

        headers = {
            'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}'
        }

        response = requests.post(url, files=files, data=data, headers=headers)

        if response.status_code == 200:
            result = response.json()

            # Extract text from successful results
            extracted_texts = []
            for page_result in result.get('results', []):
                if page_result.get('success') and page_result.get('message'):
                    content = page_result['message']['choices'][0]['message']['content']
                    try:
                        # Try to parse as JSON if it's structured output
                        parsed_content = json.loads(content)
                        text = parsed_content.get('natural_text', content)
                    except json.JSONDecodeError:
                        text = content
                    extracted_texts.append(text)
                elif not page_result.get('success'):
                    print(f"Error processing {page_result.get('filename', 'unknown')}: {page_result.get('error', 'Unknown error')}")

            return '\n'.join(extracted_texts)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def write_pdf(path, file_name, content):
    file_name = file_name.replace("/", "-")
    path = os.path.join(path, file_name)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "wb") as f:
        f.write(content)
    return path

def write_text(path, file_name, content):
    file_name = file_name.replace("/", "-")
    path = os.path.join(path, file_name)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path