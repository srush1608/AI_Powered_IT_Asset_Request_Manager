from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from backend.database import Base, engine, get_db
from backend.routes import auth, chatbot
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from backend.chatbot_graph import Graph, StateManager, AssetAvailabilityTool
from sqlalchemy.orm import Session
from pydantic import BaseModel

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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

@app.post("/api/chat/")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        message = request.query
        
        if not message:
            raise HTTPException(status_code=400, detail="Query parameter is missing")

        # Initialize tools and manager
        availability_tool = AssetAvailabilityTool()
        state_manager = StateManager()

        # Initialize the Graph class with required arguments
        graph = Graph(availability_tool=availability_tool, state_manager=state_manager)

        # Process message
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
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Entry point for the application."""
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()



























# # main.py

# # from fastapi import FastAPI, Form, HTTPException, Depends
# # from fastapi.responses import HTMLResponse, RedirectResponse
# # from backend.chatbot_graph import process_message, create_state_manager
# # from sqlalchemy.orm import Session
# # from pydantic import BaseModel

# # # FastAPI app initialization
# # app = FastAPI()

# # # Define request model for the chatbot query
# # class ChatRequest(BaseModel):
# #     query: str

# # # Define route for processing chatbot messages
# # @app.post("/api/chat/")
# # async def chat_endpoint(
# #     request: ChatRequest, 
# #     db: Session = Depends(get_db)
# # ):
# #     try:
# #         message = request.query
# #         if not message:
# #             raise HTTPException(status_code=400, detail="Query parameter is missing")

# #         # Initialize the state manager
# #         state = create_state_manager()

# #         # Process message and get response
# #         result = await process_message(state, message)

# #         # Get the last response from conversation history
# #         if result['conversation_history']:
# #             last_message = result['conversation_history'][-1]
# #             return {
# #                 "response": last_message["content"],
# #                 "status": "success",
# #                 "stage": result['conversation_stage']
# #             }
        
# #         return {
# #             "response": "I apologize, but I couldn't process your request.",
# #             "status": "error",
# #             "stage": "error"
# #         }

# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error occurred: {e}")





# from fastapi import FastAPI, Form, HTTPException, Depends
# from fastapi.staticfiles import StaticFiles
# from backend.database import Base, engine, get_db
# from backend.routes import auth, chatbot
# import os
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from fastapi.responses import HTMLResponse, RedirectResponse
# from starlette.requests import Request
# from starlette.middleware.sessions import SessionMiddleware
# from backend.chatbot_graph import Graph, StateManager, AssetAvailabilityTool
# from sqlalchemy.orm import Session
# from pydantic import BaseModel

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create database tables
# Base.metadata.create_all(bind=engine)

# # Include routers
# app.include_router(auth.router, prefix="/api")
# app.include_router(chatbot.router, prefix="/api")

# # Mount static files
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# # Add session middleware
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# # Define request model
# class ChatRequest(BaseModel):
#     query: str

# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     """Login Page."""
#     return HTMLResponse(content=open("frontend/index.html").read(), status_code=200)

# @app.get("/chatbot", response_class=HTMLResponse)
# async def chatbot_page(request: Request):
#     """Chatbot Interface."""
#     user = request.session.get("user")
#     if not user:
#         return RedirectResponse("/", status_code=302)
#     return HTMLResponse(content=open("frontend/chatbot.html").read(), status_code=200)

# @app.post("/api/chat/")
# async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
#     try:
#         message = request.query
        
#         if not message:
#             raise HTTPException(status_code=400, detail="Query parameter is missing")

#         # Initialize tools and manager
#         availability_tool = AssetAvailabilityTool()
#         state_manager = StateManager()

#         # Initialize the Graph class with required arguments
#         graph = Graph(availability_tool=availability_tool, state_manager=state_manager)

#         # Process message
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
#         raise HTTPException(status_code=500, detail=str(e))

# def main():
#     """Entry point for the application."""
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# if __name__ == "__main__":
#     main()
















# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.staticfiles import StaticFiles
# from backend.database import Base, engine, get_db
# from backend.routes import auth, chatbot
# import os
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from fastapi.responses import HTMLResponse, RedirectResponse
# from starlette.requests import Request
# from starlette.middleware.sessions import SessionMiddleware
# from backend.chatbot_graph import AssetManagementGraph, AssetAvailabilityTool
# from sqlalchemy.orm import Session
# from pydantic import BaseModel

# # Load environment variables from .env file
# load_dotenv()

# # Secret key from environment variables
# SECRET_KEY = os.getenv("SECRET_KEY")

# # Create FastAPI instance
# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create the database tables
# Base.metadata.create_all(bind=engine)

# # Include routers for auth and chatbot
# app.include_router(auth.router, prefix="/api")
# app.include_router(chatbot.router, prefix="/api")

# # Mount static files (frontend files)
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# # Add session middleware for session management
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# # Define the request model for chatbot interactions
# class ChatRequest(BaseModel):
#     query: str

# # Root endpoint to serve login page
# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     """Serve login page."""
#     return HTMLResponse(content=open("frontend/index.html").read(), status_code=200)

# # Chatbot page for users
# @app.get("/chatbot", response_class=HTMLResponse)
# async def chatbot_page(request: Request):
#     """Serve the chatbot interface."""
#     user = request.session.get("user")
#     if not user:
#         return RedirectResponse("/", status_code=302)
#     return HTMLResponse(content=open("frontend/chatbot.html").read(), status_code=200)

# # Post request to handle chatbot messages
# @app.post("/api/chat/")
# async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
#     try:
#         message = request.query
        
#         if not message:
#             raise HTTPException(status_code=400, detail="Query parameter missing")

#         # Initialize AssetAvailabilityTool and AssetManagementGraph
#         availability_tool = AssetAvailabilityTool()
#         availability_tool.set_db(db)  # Set DB session for the tool

#         # Initialize Graph with the availability tool
#         graph = AssetManagementGraph(db)

#         # Process the message and get the result
#         result = await graph.process_message(message)

#         # Check if conversation history exists and return the latest message
#         if result.get('conversation_history'):
#             last_message = result['conversation_history'][-1]
#             return {
#                 "response": last_message["content"],
#                 "status": "success",
#                 "stage": result['conversation_stage']
#             }
        
#         return {
#             "response": "Could not process your request.",
#             "status": "error",
#             "stage": "error"
#         }

#     except Exception as e:
#         # Handle any errors during the process
#         raise HTTPException(status_code=500, detail=str(e))

# # Entry point for running the FastAPI application
# def main():
#     """Run the FastAPI app."""
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# if __name__ == "__main__":
#     main()

