
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.chatbot_graph import StateManager, Graph, AssetAvailabilityTool
from backend.database import SessionLocal
from sqlalchemy.orm import Session
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
        
        logging.debug(f"Received message: {message}")
        
        if not message:
            raise HTTPException(status_code=400, detail="Query parameter is missing")
        
        # Initialize chatbot components
        availability_tool = AssetAvailabilityTool()
        graph = Graph(availability_tool=availability_tool)

        # Process message and get response
        result = await graph.process_message(message)

        # Get the last response from conversation history
        if result['conversation_history']:
            last_message = result['conversation_history'][-1]
            return {
                "response": last_message["content"],
                "status": "success",
                "stage": result['conversation_stage']
            }
        
        return {
            "response": "I apologize, but I couldn't process your request.",
            "status": "error",
            "stage": "error"
        }

    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")












# from fastapi import APIRouter, Depends, HTTPException, Request
# from backend.chatbot_graph import StateManager, Graph, AssetAvailabilityTool
# from backend.database import SessionLocal
# from sqlalchemy.orm import Session
# import logging

# router = APIRouter()
# logging.basicConfig(level=logging.DEBUG)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/chat/")
# async def chatbot_interaction(request: Request, db: Session = Depends(get_db)):
#     try:
#         body = await request.json()
#         message = body.get("query")
        
#         logging.debug(f"Received message: {message}")
        
#         if not message:
#             raise HTTPException(status_code=400, detail="Query parameter is missing")
        
#         # Initialize chatbot components
#         availability_tool = AssetAvailabilityTool()
#         graph = Graph(availability_tool=availability_tool)

#         # Process message and get response
#         result = await graph.process_message(message)

#         # Get the last response from conversation history
#         if result['conversation_history']:
#             last_message = result['conversation_history'][-1]
#             return {
#                 "response": last_message["content"],
#                 "status": "success",
#                 "stage": result['conversation_stage']
#             }
        
#         return {
#             "response": "I apologize, but I couldn't process your request.",
#             "status": "error",
#             "stage": "error"
#         }

#     except Exception as e:
#         logging.error(f"Error processing chat request: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")