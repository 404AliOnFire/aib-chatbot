import json

# --- عدّل اسم الملف هنا إذا لزم الأمر ---
file_to_check = 'errors_to_fix.json'
# ------------------------------------

# قائمة لتخزين كل الأخطاء اللي بنلاقيها
all_errors = []
# قائمة جديدة لتخزين أرقام أسطر بداية كل سجل
record_start_lines = []

def validate_record(record, index):
    """
    هذه الوظيفة تفحص سجلاً واحداً (كائن JSON واحد)
    وتتأكد من أن هيكله صحيح 100%. (نفس الوظيفة السابقة)
    """
    errors = []
    
    if not isinstance(record, dict):
        errors.append(f"  -> العنصر ليس كائن (object) بل هو من نوع '{type(record).__name__}'.")
        return errors

    expected_keys = {"question", "context", "answers"}
    record_keys = set(record.keys())
    if record_keys != expected_keys:
        errors.append(f"  -> المفاتيح الرئيسية غير صحيحة. المتوقع: {expected_keys}, الموجود: {record_keys}")

    if 'question' in record and not isinstance(record['question'], str):
        errors.append(f"  -> الخطأ في 'question': يجب أن يكون من نوع 'نص' (str), لكن النوع الحالي هو '{type(record['question']).__name__}'.")
    
    if 'context' in record and not isinstance(record['context'], str):
        errors.append(f"  -> الخطأ في 'context': يجب أن يكون من نوع 'نص' (str), لكن النوع الحالي هو '{type(record['context']).__name__}'.")

    if 'answers' in record and not isinstance(record['answers'], dict):
        errors.append(f"  -> الخطأ في 'answers': يجب أن يكون من نوع 'كائن' (dict), لكن النوع الحالي هو '{type(record['answers']).__name__}'.")
        return errors

    answers_obj = record.get('answers', {})
    expected_answers_keys = {"text", "answer_start"}
    answers_keys = set(answers_obj.keys())

    if answers_keys != expected_answers_keys:
        errors.append(f"  -> الخطأ في 'answers': المفاتيح الداخلية غير صحيحة. المتوقع: {expected_answers_keys}, الموجود: {answers_keys}")

    if 'text' in answers_obj and not isinstance(answers_obj['text'], list):
        errors.append(f"  -> الخطأ في 'answers' -> 'text': يجب أن يكون من نوع 'قائمة' (list), لكن النوع الحالي هو '{type(answers_obj['text']).__name__}'.")
        
    if 'answer_start' in answers_obj and not isinstance(answers_obj['answer_start'], list):
        errors.append(f"  -> الخطأ في 'answers' -> 'answer_start': يجب أن يكون من نوع 'قائمة' (list), لكن النوع الحالي هو '{type(answers_obj['answer_start']).__name__}'.")

    return errors

# ----- البرنامج الرئيسي يبدأ من هنا -----
try:
    print(f"جاري فحص هيكل الملف: {file_to_check} ...")
    
    # --- الجزء الجديد: تحديد أرقام الأسطر ---
    with open(file_to_check, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # نبحث عن الأسطر التي تبدأ بـ "{" وتكون في بداية السجل
        # هذا يفترض أن الملف منسق بشكل جيد (pretty-printed)
        in_main_list = False
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith('['):
                in_main_list = True
            
            # إذا كنا داخل القائمة الرئيسية ووجدنا سطراً يبدأ بـ {، فهذا بداية سجل جديد
            if in_main_list and stripped_line.startswith('{'):
                record_start_lines.append(i + 1) # نضيف 1 لأن الأسطر تبدأ من 1 وليس 0
    # -----------------------------------------

    # نعيد فتح الملف لتحميله كـ JSON وفحصه
    with open(file_to_check, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("\n🚨 خطأ أساسي: الملف لا يبدأ بقائمة [].")
    else:
        # نمر على كل سجل في القائمة الرئيسية
        for index, record in enumerate(data):
            errors_found = validate_record(record, index)
            if errors_found:
                # نحاول الحصول على رقم السطر المطابق لرقم السجل
                line_number_info = "غير محدد"
                if index < len(record_start_lines):
                    line_number_info = f"يبدأ تقريباً من السطر {record_start_lines[index]}"
                
                # نضيف رسالة الخطأ مع رقم السجل ورقم السطر
                all_errors.append(f"- في السجل رقم [{index}] ({line_number_info}):")
                all_errors.extend(errors_found)

    # بعد الانتهاء من الفحص، نعرض النتائج
    if not all_errors:
        print("\n✅ كل شيء تمام! هيكل البيانات في الملف مطابق للمطلوب.")
    else:
        print("\n🚨 تم العثور على أخطاء في هيكل البيانات!")
        for error_message in all_errors:
            print(error_message)

except FileNotFoundError:
    print(f"\nخطأ: الملف '{file_to_check}' غير موجود.")
except json.JSONDecodeError as e:
    print(f"\nخطأ: الملف '{file_to_check}' ليس ملف JSON صالحًا. يوجد خطأ بالقرب من السطر {e.lineno}، العمود {e.colno}.")
except Exception as e:
    print(f"\nحدث خطأ غير متوقع: {e}")