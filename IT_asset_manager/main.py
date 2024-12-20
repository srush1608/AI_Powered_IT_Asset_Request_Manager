from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from backend.database import Base, engine, get_db
from backend.routes import auth
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from backend.chatbot_graph import Graph, StateManager, AssetAvailabilityTool, DynamicChatNode, InvalidQueryNode
from sqlalchemy.orm import Session
from pydantic import BaseModel

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include auth router
app.include_router(auth.router, prefix="/api")

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Initialize state manager for chatbot
state_manager = StateManager()

# Define request model
class ChatRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login Page."""
    return HTMLResponse(content=open("frontend/index.html").read(), status_code=200)

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    """Chatbot Interface."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/", status_code=302)
    return HTMLResponse(content=open("frontend/chatbot.html").read(), status_code=200)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        message = request.query
        
        if not message:
            raise HTTPException(status_code=400, detail="Query parameter is missing")

        # Initialize chatbot components
        graph = Graph()
        availability_tool = AssetAvailabilityTool()
        chat_node = DynamicChatNode(availability_tool)
        invalid_query_node = InvalidQueryNode()

        # Set up graph
        graph.add_node("dynamic_chat", chat_node)
        graph.add_node("invalid_query", invalid_query_node)
        
        # Update edge conditions
        graph.add_edge(
            "dynamic_chat", 
            "dynamic_chat", 
            condition=lambda state, msg: any(word in msg.lower() for word in ["hi", "hello", "laptop", "monitor", "keyboard", "mouse"])
        )
        graph.add_edge(
            "dynamic_chat",
            "invalid_query",
            condition=lambda state, msg: not any(word in msg.lower() for word in ["hi", "hello", "laptop", "monitor", "keyboard", "mouse"])
        )

        # Get or create state for user
        state = state_manager.get_or_create(
            employee_id="temp_id",  # You can update this with actual user ID
            user_email="temp@example.com"  # You can update this with actual user email
        )

        # Process message
        result = await graph.arun(state, message)

        # Get the last response from conversation history
        if result.conversation_history:
            last_message = result.conversation_history[-1]
            return {
                "response": last_message["content"],
                "status": result.status,
                "stage": result.conversation_stage
            }
        
        return {
            "response": "I apologize, but I couldn't process your request.",
            "status": "error",
            "stage": "error"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)