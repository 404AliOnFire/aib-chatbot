# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

model_path = "."

qa_pipeline = pipeline(
    "question-answering",
    model=model_path,
    tokenizer=model_path
)

app = FastAPI(
    title="Bank QA API",
    description="API for answering banking questions."
)

# Allow requests from any origin.
# This is suitable for development, but in production it is better to specify allowed domains.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    context: str


@app.post("/ask")
def ask_question(request: QuestionRequest):
    result = qa_pipeline(
        question=request.question,
        context=request.context
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "score": result["score"]
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to the Bank QA API. Go to /docs to test."
    }
