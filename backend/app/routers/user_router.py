from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users Authentication"])


class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    national_id: str
    age: int

@router.post("/register")
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
   
    existing_user = db.query(User).filter(
        (User.national_id == user_data.national_id) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="National ID or Email already registered!")

    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=user_data.password, 
        phone=user_data.phone,
        national_id=user_data.national_id,
        age=user_data.age
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Account created successfully", 
        "user_id": new_user.user_id,
        "name": new_user.name
    }
    
class UserLoginRequest(BaseModel):
    national_id: str
    password: str


@router.post("/login")
def login_user(login_data: UserLoginRequest, db: Session = Depends(get_db)):
  
    user = db.query(User).filter(User.national_id == login_data.national_id).first()
    
    
    if not user or user.password_hash != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid National ID or Password")
    
   
    return {
        "message": "Login successful",
        "user_id": user.user_id,
        "name": user.name,
        "role": user.role
    }