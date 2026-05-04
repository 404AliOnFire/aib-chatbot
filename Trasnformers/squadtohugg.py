# script3_squad_to_huggingface.py

import json

# Input and output files
squad_format_file = 'QA.json'
huggingface_format_file = 'huggingface_data.json'

print("Starting conversion from SQuAD format to Hugging Face format...")
print(f"Input file: {squad_format_file}")

try:
    with open(squad_format_file, 'r', encoding='utf-8') as f:
        squad_data = json.load(f)
except Exception as e:
    print(f"Error reading the file. Make sure it exists. Error: {e}")
    exit()

# This list will contain all questions in the new format
huggingface_list = []

# Iterate through the nested SQuAD structure
# First level: data
for topic in squad_data['data']:

    # Second level: paragraphs
    for paragraph in topic['paragraphs']:
        context = paragraph['context']

        # Third level: qas, which contains questions and answers
        for qa in paragraph['qas']:
            question = qa['question']
            q_id = qa['id']

            # Start the conversion process
            # Extract answer texts and their start positions
            texts = []
            starts = []

            # Iterate over the list of answers, even if there is only one
            for answer in qa['answers']:
                texts.append(answer['text'])
                starts.append(answer['answer_start'])

            # Build the answers object in the new format
            hf_answers = {
                "text": texts,
                "answer_start": starts
            }

            # Combine everything into one flat object
            flat_item = {
                "id": q_id,
                "context": context,
                "question": question,
                "answers": hf_answers
            }

            huggingface_list.append(flat_item)
            # End the conversion process

# Save the final list to a new JSON file
with open(huggingface_format_file, 'w', encoding='utf-8') as f:
    json.dump(huggingface_list, f, ensure_ascii=False, indent=4)

print("\n--- Conversion completed successfully ---")
print(f"Converted and processed questions: {len(huggingface_list)}")
print(f"Final Hugging Face format file saved to: {huggingface_format_file}")
