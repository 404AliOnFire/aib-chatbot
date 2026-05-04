# main.py - النسخة النهائية مع حل مشكلة CORS

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
# --- 1. استيراد وسيط CORS ---
from fastapi.middleware.cors import CORSMiddleware

# --- تحميل النموذج (لا تغيير هنا) ---
model_path = "."
qa_pipeline = pipeline("question-answering", model=model_path, tokenizer=model_path)
app = FastAPI(title="Bank QA API", description="API for answering banking questions.")

# --- 2. إضافة وسيط CORS إلى التطبيق ---
# هذا الكود يخبر الخادم بأن يسمح بالاتصالات من أي مصدر (*)
# وهذا مناسب لمرحلة التطوير.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # السماح بكل الطرق (GET, POST, etc.)
    allow_headers=["*"], # السماح بكل الـ headers
)
# --- نهاية الإضافة ---

# --- بقية الكود (لا تغيير هنا) ---
class QuestionRequest(BaseModel):
    question: str
    context: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    result = qa_pipeline(question=request.question, context=request.context)
    return {
        "question": request.question,
        "answer": result['answer'],
        "score": result['score']
    }

@app.get("/")
def root():
    return {"message": "Welcome to the Bank QA API! Go to /docs to test."}