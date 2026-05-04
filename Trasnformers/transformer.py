# script1_fix_data.py

import json

input_file = 'input.json'
output_file = 'cleaned_data.json'

print(f"Starting data cleaning for file: {input_file}")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
except Exception as e:
    print(f"Error reading the file. Make sure it exists and is valid JSON. Error: {e}")
    exit()

cleaned_entries = []
fixed_count = 0
error_count = 0

for item in all_data:
    is_fixed = False

    # Create a copy of the item to avoid modifying the original while processing
    new_item = item.copy()
    answers_data = new_item.get('answers')

    if not isinstance(answers_data, (dict, list)):
        error_count += 1
        continue

    final_text_list = None
    final_start_list = None

    # Case 1: answers is a list and needs to be converted
    if isinstance(answers_data, list):
        if answers_data and isinstance(answers_data[0], dict):
            first_answer = answers_data[0]
            text = first_answer.get('text')
            start = first_answer.get('answer_start')

            if isinstance(text, str):
                final_text_list = [text]

            if isinstance(start, int):
                final_start_list = [start]

            if isinstance(start, list):
                final_start_list = start

            is_fixed = True

    # Case 2: answers is a dictionary and its structure needs to be checked
    elif isinstance(answers_data, dict):
        text = answers_data.get('text')

        # Look for either answer_start or the incorrect answer__start key
        start = answers_data.get('answer_start') or answers_data.get('answer__start')

        if answers_data.get('answer__start'):
            is_fixed = True

        # Make sure text is a list
        if isinstance(text, str):
            final_text_list = [text]
            is_fixed = True
        elif isinstance(text, list):
            final_text_list = text

        # Make sure answer_start is a list
        if isinstance(start, int):
            final_start_list = [start]
            is_fixed = True
        elif isinstance(start, list):
            final_start_list = start

    # If the data was extracted successfully, build the correct structure
    if final_text_list is not None and final_start_list is not None:
        new_item['answers'] = {
            "text": final_text_list,
            "answer_start": final_start_list
        }

        # Remove the incorrect key if it exists
        if 'answer__start' in new_item['answers']:
            del new_item['answers']['answer__start']

        cleaned_entries.append(new_item)

        if is_fixed:
            fixed_count += 1
    else:
        error_count += 1

# Save the cleaned data to a new file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned_entries, f, ensure_ascii=False, indent=4)

print("\n--- Cleaning completed ---")
print(f"Processed and cleaned questions: {len(cleaned_entries)}")
print(f"Questions that were fixed: {fixed_count}")
print(f"Questions skipped because they could not be fixed: {error_count}")
print(f"Cleaned data saved to: {output_file}")
