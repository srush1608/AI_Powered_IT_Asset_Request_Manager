from fastapi import FastAPI, HTTPException
from app.chatbot import get_bot_response

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the IT Asset Request Chatbot"}

@app.post("/chat/")
def chatbot_interaction(user_message: str):
    if not user_message:
        raise HTTPException(status_code=400, detail="User message is required.")
    response = get_bot_response(user_message)
    return {"user_message": user_message, "bot_response": response}
