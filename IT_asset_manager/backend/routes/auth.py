from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import crud, models, database, security
from pydantic import BaseModel
import bcrypt
# import PyJWT as jwt
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserInLogin(BaseModel):
    email: str  
    password: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def authenticate_user(email: str, password: str, db: Session):
    employee = db.query(models.Employee).filter(models.Employee.email == email).first()

    if employee is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not security.verify_password(employee.password, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return employee

@router.post("/login/")
def login(user: UserInLogin, db: Session = Depends(database.get_db)):
    print(f"Attempting to log in user: {user.email}")
    db_user = crud.get_user_by_email(db, email=user.email)
    
    if db_user is None:
        print("User not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    authenticated_user = authenticate_user(user.email, user.password, db)
    print("User authenticated successfully")
    
    access_token = create_access_token(data={"sub": authenticated_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/chat/")
# async def chat_endpoint(query: dict, db: Session = Depends(database.get_db)):
#     # Your chat handling logic here
#     return {"response": "This is a response from the chat endpoint."}