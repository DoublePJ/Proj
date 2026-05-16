import pandas as pd
from pythainlp.tokenize import word_tokenize
from rouge_score import rouge_scorer
from bert_score import score
import warnings
warnings.filterwarnings("ignore")

def calculate_token_f1(pred, truth):
    """คำนวณ Token F1-Score โดยใช้ PyThaiNLP ตัดคำ"""
    pred_tokens = set(word_tokenize(str(pred), engine="newmm"))
    truth_tokens = set(word_tokenize(str(truth), engine="newmm"))
    
    common_tokens = pred_tokens.intersection(truth_tokens)
    
    if len(common_tokens) == 0:
        return 0.0
    
    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(truth_tokens)
    
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1

def calculate_rouge_l(pred, truth):
    """คำนวณ ROUGE-L โดยต้องเว้นวรรคคำภาษาไทยก่อนส่งให้ Scorer"""
    pred_spaced = " ".join(word_tokenize(str(pred), engine="newmm"))
    truth_spaced = " ".join(word_tokenize(str(truth), engine="newmm"))
    
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)
    scores = scorer.score(truth_spaced, pred_spaced)
    return scores['rougeL'].fmeasure

def run_nlp_evaluation(csv_file_path):
    print(f">>> กำลังโหลดข้อมูลจากไฟล์: {csv_file_path}")
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ CSV! กรุณาตรวจสอบชื่อไฟล์และที่อยู่ให้ถูกต้อง")
        return

    # 🟢 แก้ไขจุดที่ 1: เปลี่ยนชื่อคอลัมน์ในการตรวจสอบให้ตรงกับ Ragas เวอร์ชันใหม่
    if 'response' not in df.columns or 'reference' not in df.columns:
        print("❌ ไฟล์ CSV ไม่มีคอลัมน์ 'response' และ 'reference'")
        print(f"คอลัมน์ที่มีในไฟล์: {df.columns.tolist()}")
        return

    # 🟢 แก้ไขจุดที่ 2: ดึงข้อมูลจากคอลัมน์ 'response' และ 'reference'
    answers = df['response'].fillna("").tolist()
    truths = df['reference'].fillna("").tolist()

    print("\n>>> 1. กำลังคำนวณ Token F1-Score และ ROUGE-L...")
    token_f1_scores = []
    rouge_l_scores = []
    
    for ans, truth in zip(answers, truths):
        token_f1_scores.append(calculate_token_f1(ans, truth))
        rouge_l_scores.append(calculate_rouge_l(ans, truth))
        
    avg_token_f1 = sum(token_f1_scores) / len(token_f1_scores)
    avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores)

    print(">>> 2. กำลังคำนวณ BERTScore (อาจใช้เวลาโหลดโมเดลภาษา 1-2 นาที)...")
    P, R, F1 = score(answers, truths, lang="th", verbose=True)
    avg_bert_f1 = F1.mean().item()

    print("\n" + "="*50)
    print("🏆 สรุปผลการประเมินประสิทธิภาพด้านภาษา (NLP Metrics)")
    print("="*50)
    print(f"1. Token F1-Score (คำตรงกัน)      : {avg_token_f1:.4f}")
    print(f"2. ROUGE-L (โครงสร้างประโยค)      : {avg_rouge_l:.4f}")
    print(f"3. BERTScore F1 (ความหมายตรงกัน) : {avg_bert_f1:.4f}")
    print("="*50)

    df['token_f1'] = token_f1_scores
    df['rouge_l'] = rouge_l_scores
    df['bertscore_f1'] = F1.tolist()
    
    output_filename = csv_file_path.replace(".csv", "_with_nlp.csv")
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"✅ บันทึกคะแนนรายข้อลงในไฟล์ {output_filename} เรียบร้อยแล้ว!")

if __name__ == "__main__":
    run_nlp_evaluation("ragas_results_typhoon.csv")