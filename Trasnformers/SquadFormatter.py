# script2_convert_to_squad.py

import json

input_file = 'cleaned_data.json'
output_file = 'squad_formatted_output.json'

print(f"Starting conversion of cleaned file {input_file} to SQuAD format")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        cleaned_data = json.load(f)
except Exception as e:
    print(f"Error reading the file. Make sure you run the first script first. Error: {e}")
    exit()

contexts = {}
question_id_counter = 0

for item in cleaned_data:
    context = item['context']
    question = item['question']
    answers = item['answers']

    answer_text = answers['text'][0]
    answer_start = answers['answer_start'][0]

    qa_item = {
        "id": f"q_{question_id_counter}",
        "question": question,
        "answers": [
            {
                "text": answer_text,
                "answer_start": answer_start
            }
        ]
    }

    question_id_counter += 1

    if context not in contexts:
        contexts[context] = []

    contexts[context].append(qa_item)

paragraphs = []

for context_text, qas in contexts.items():
    paragraphs.append({
        "context": context_text,
        "qas": qas
    })

final_squad_data = {
    "data": [
        {
            "title": "My AIB Dataset",
            "paragraphs": paragraphs
        }
    ]
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_squad_data, f, ensure_ascii=False, indent=4)

print("\n--- Conversion completed ---")
print(f"Unique context paragraphs grouped: {len(paragraphs)}")
print(f"Questions converted successfully: {question_id_counter}")
print(f"Final SQuAD format file saved to: {output_file}")
