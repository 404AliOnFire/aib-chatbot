# script1_fix_data.py

import json

input_file = 'input.json'
output_file = 'cleaned_data.json'

print(f"بدء عملية تنظيف الملف: {input_file}")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
except Exception as e:
    print(f"خطأ في قراءة الملف. تأكد من أنه موجود وبصيغة JSON. الخطأ: {e}")
    exit()

cleaned_entries = []
fixed_count = 0
error_count = 0

for item in all_data:
    is_fixed = False
    
    # نسخة جديدة من العنصر لكي لا نعدل على الأصلي أثناء المرور عليه
    new_item = item.copy()
    answers_data = new_item.get('answers')

    if not isinstance(answers_data, (dict, list)):
        error_count += 1
        continue

    final_text_list = None
    final_start_list = None

    # الحالة 1: answers عبارة عن قائمة (list) - يجب تحويلها
    if isinstance(answers_data, list):
        if answers_data and isinstance(answers_data[0], dict):
            first_answer = answers_data[0]
            text = first_answer.get('text')
            start = first_answer.get('answer_start')

            if isinstance(text, str): final_text_list = [text]
            if isinstance(start, int): final_start_list = [start]
            if isinstance(start, list): final_start_list = start
            is_fixed = True

    # الحالة 2: answers عبارة عن كائن (dict) - يجب التأكد من هيكله
    elif isinstance(answers_data, dict):
        text = answers_data.get('text')
        # البحث عن answer_start أو answer__start
        start = answers_data.get('answer_start') or answers_data.get('answer__start')
        
        if answers_data.get('answer__start'):
            is_fixed = True

        # تأكد أن النص قائمة
        if isinstance(text, str):
            final_text_list = [text]
            is_fixed = True
        elif isinstance(text, list):
            final_text_list = text

        # تأكد أن رقم البداية قائمة
        if isinstance(start, int):
            final_start_list = [start]
            is_fixed = True
        elif isinstance(start, list):
            final_start_list = start
            
    # إذا نجحنا في استخلاص البيانات، نبني الكائن الصحيح
    if final_text_list is not None and final_start_list is not None:
        new_item['answers'] = {
            "text": final_text_list,
            "answer_start": final_start_list
        }
        # نحذف المفتاح الخاطئ إذا كان موجوداً
        if 'answer__start' in new_item['answers']:
            del new_item['answers']['answer__start']

        cleaned_entries.append(new_item)
        if is_fixed:
            fixed_count += 1
    else:
        error_count += 1

# حفظ البيانات النظيفة في ملف جديد
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned_entries, f, ensure_ascii=False, indent=4)

print("\n--- اكتمل التنظيف ---")
print(f"✅ تم إصلاح ومعالجة: {len(cleaned_entries)} سؤال")
print(f"🔧 منها أسئلة تم إصلاحها: {fixed_count}")
print(f"❌ أسئلة تم تخطيها لعدم القدرة على إصلاحها: {error_count}")
print(f"💾 تم حفظ البيانات النظيفة في: {output_file}")