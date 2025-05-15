from fastapi import APIRouter
import openai

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/query")
def chat_query(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response["choices"][0]["message"]["content"]}
