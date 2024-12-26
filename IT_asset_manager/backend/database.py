from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Database connection
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define table for saving the chat history and requests
class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    conversation_history = Column(JSON)
    current_request = Column(JSON)

class Asset(Base):
    __tablename__ = 'assets'

    asset_id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String, index=True)
    configuration = Column(String)
    category = Column(String)
    request_status = Column(String)


# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to save the chat history to the database
def save_chat_history(db, conversation_history, current_request):
    chat_history_entry = ChatHistory(conversation_history=conversation_history, current_request=current_request)
    db.add(chat_history_entry)
    db.commit()
    db.refresh(chat_history_entry)
    return chat_history_entry
