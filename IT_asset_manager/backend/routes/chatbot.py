# backend/routes/chatbot.py

from fastapi import APIRouter, Depends, HTTPException, Request
from backend.chatbot_graph import StateManager, Graph, AssetAvailabilityTool, DynamicChatNode, InvalidQueryNode
from backend.database import SessionLocal
from sqlalchemy.orm import Session
import json
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat/")
async def chatbot_interaction(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        message = body.get("query")
        
        if not message:
            raise HTTPException(status_code=400, detail="Query parameter is missing")
        
        # Initialize chatbot components
        state_manager = StateManager()
        availability_tool = AssetAvailabilityTool()
        
        # Create graph
        graph = Graph()
        chat_node = DynamicChatNode(availability_tool)
        invalid_query_node = InvalidQueryNode()
        
        # Add nodes and edges
        graph.add_node("dynamic_chat", chat_node)
        graph.add_node("invalid_query", invalid_query_node)
        
        # Add edges with conditions
        graph.add_edge(
            "dynamic_chat", 
            "dynamic_chat", 
            lambda state, msg: any(word in msg.lower() for word in ["hi", "hello", "laptop", "monitor", "keyboard", "mouse"])
        )
        graph.add_edge(
            "dynamic_chat",
            "invalid_query",
            lambda state, msg: not any(word in msg.lower() for word in ["hi", "hello", "laptop", "monitor", "keyboard", "mouse"])
        )
        
        # Process message through graph
        state = state_manager.get_or_create(
            employee_id="E1234",  # Replace with actual employee ID from token
            user_email="john.deo@example.com"  # Replace with actual email from token
        )
        
        result = await graph.arun(state, message)
        
        # Return the last message from conversation history
        if result.conversation_history:
            last_message = result.conversation_history[-1]
            return {"response": last_message["content"]}
        else:
            return {"response": "I apologize, but I couldn't process your request."}
            
    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")