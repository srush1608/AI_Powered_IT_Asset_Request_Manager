import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.database import Base, engine
from backend.routes import auth
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Serve the frontend folder containing the IT Asset Management UI
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app.include_router(auth.router, prefix="/api")

