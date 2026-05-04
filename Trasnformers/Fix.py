import json

# ملف الإدخال والإخراج
input_file = "QA.json"
output_file = "QA_fixed.json"

# اقرأ البيانات
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

fixed_data = {"data": []}

# افترض إنو البيانات جايه مثل SQuAD: data -> paragraphs -> qas
for article in data["data"]:
    new_article = {"title": article.get("title", ""), "paragraphs": []}
    for para in article["paragraphs"]:
        new_para = {"context": para["context"], "qas": []}
        for qa in para["qas"]:
            answers = qa.get("answers", {})
            
            # إذا مش dict خلّيه dict
            if not isinstance(answers, dict):
                answers = {"text": [], "answer_start": []}

            # تأكد text لست
            texts = answers.get("text", [])
            if isinstance(texts, str):
                texts = [texts]
            elif not isinstance(texts, list):
                texts = []

            # تأكد answer_start لست
            starts = answers.get("answer_start", [])
            if isinstance(starts, int):
                starts = [starts]
            elif not isinstance(starts, list):
                starts = []

            new_qa = {
                "id": qa.get("id", ""),
                "question": qa["question"],
                "answers": {
                    "text": texts,
                    "answer_start": starts
                }
            }
            new_para["qas"].append(new_qa)
        new_article["paragraphs"].append(new_para)
    fixed_data["data"].append(new_article)

# احفظ الملف الجديد
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(fixed_data, f, ensure_ascii=False, indent=2)

print(f"✅ Saved cleaned dataset at {output_file}")
