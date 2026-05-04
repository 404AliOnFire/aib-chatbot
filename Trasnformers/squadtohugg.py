# script3_squad_to_huggingface.py

import json

# المدخلات والمخرجات
squad_format_file = 'QA.json'
huggingface_format_file = 'huggingface_data.json'

print(f"بدء تحويل الملف من صيغة SQuAD إلى صيغة Hugging Face...")
print(f"الملف المدخل: {squad_format_file}")

try:
    with open(squad_format_file, 'r', encoding='utf-8') as f:
        squad_data = json.load(f)
except Exception as e:
    print(f"خطأ في قراءة الملف. تأكد من وجوده. الخطأ: {e}")
    exit()

# هذه القائمة ستحتوي على كل الأسئلة بالصيغة الجديدة
huggingface_list = []

# المرور على الهيكل المتداخل لـ SQuAD
# المستوى الأول: data
for topic in squad_data['data']:
    # المستوى الثاني: paragraphs
    for paragraph in topic['paragraphs']:
        context = paragraph['context']
        
        # المستوى الثالث: qas (الأسئلة والأجوبة)
        for qa in paragraph['qas']:
            question = qa['question']
            q_id = qa['id']
            
            # --- بداية عملية التحويل ---
            # استخلاص نصوص الإجابات وأماكن البداية
            texts = []
            starts = []
            
            # المرور على قائمة الإجابات (حتى لو كانت واحدة)
            for answer in qa['answers']:
                texts.append(answer['text'])
                starts.append(answer['answer_start'])
            
            # بناء كائن answers بالصيغة الجديدة
            hf_answers = {
                "text": texts,
                "answer_start": starts
            }
            
            # تجميع كل شيء في كائن واحد مسطح
            flat_item = {
                "id": q_id,
                "context": context,
                "question": question,
                "answers": hf_answers
            }
            
            huggingface_list.append(flat_item)
            # --- نهاية عملية التحويل ---

# حفظ القائمة النهائية في ملف JSON جديد
with open(huggingface_format_file, 'w', encoding='utf-8') as f:
    json.dump(huggingface_list, f, ensure_ascii=False, indent=4)

print("\n--- اكتمل التحويل بنجاح! ---")
print(f"📊 تم تحويل ومعالجة {len(huggingface_list)} سؤال.")
print(f"💾 تم حفظ الملف النهائي بصيغة Hugging Face في: {huggingface_format_file}")