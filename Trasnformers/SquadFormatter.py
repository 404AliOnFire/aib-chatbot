# script2_convert_to_squad.py

import json

# لاحظ أننا نستخدم الملف الناتج من السكريبت الأول كمدخل هنا
input_file = 'cleaned_data.json' 
output_file = 'squad_formatted_output.json'

print(f"بدء تحويل الملف النظيف {input_file} إلى صيغة SQuAD")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        cleaned_data = json.load(f)
except Exception as e:
    print(f"خطأ في قراءة الملف. تأكد من تشغيل السكريبت الأول أولاً. الخطأ: {e}")
    exit()

contexts = {}
question_id_counter = 0

for item in cleaned_data:
    context = item['context']
    question = item['question']
    answers = item['answers']

    # استخلاص الإجابة من الهيكل النظيف
    answer_text = answers['text'][0]
    answer_start = answers['answer_start'][0]

    qa_item = {
        "id": f"q_{question_id_counter}",
        "question": question,
        "answers": [{
            "text": answer_text,
            "answer_start": answer_start
        }]
    }
    question_id_counter += 1

    # تجميع الأسئلة التي لها نفس الـ context
    if context not in contexts:
        contexts[context] = []
    contexts[context].append(qa_item)

# بناء الهيكل النهائي
paragraphs = []
for context_text, qas in contexts.items():
    paragraphs.append({
        "context": context_text,
        "qas": qas
    })

final_squad_data = {
    "data": [{
        "title": "My AIB Dataset",
        "paragraphs": paragraphs
    }]
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_squad_data, f, ensure_ascii=False, indent=4)

print("\n--- اكتمل التحويل النهائي ---")
print(f"📊 تم تجميع {len(paragraphs)} فقرة نصية فريدة.")
print(f"✅ تم تحويل {question_id_counter} سؤال بنجاح.")
print(f"💾 تم حفظ الملف النهائي بصيغة SQuAD في: {output_file}")