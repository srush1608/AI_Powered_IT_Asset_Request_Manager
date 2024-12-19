from fastapi import APIRouter
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Initialize ChatGroq model
llm = ChatGroq(model_name="llama3-groq-70b-8192-tool-use-preview")

@router.get("/chat")
async def chatbot(query: str):
    response = llm.query({"input": query})
    return {"response": response}
