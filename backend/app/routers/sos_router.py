from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app import models  
from app.database import get_db

router = APIRouter()


class SOSRequestCreate(BaseModel):
    user_id: int
    location: str

class SOSRequestResponse(BaseModel):
    sos_id: int
    user_id: int
    location: str
    requested_at: datetime
    status: str

    class Config:
        from_attributes = True


@router.post("/send", response_model=SOSRequestResponse)
async def send_sos_signal(request: SOSRequestCreate, db: Session = Depends(get_db)):
   
    new_sos =models.sos_request.SoSRequest(
        user_id=request.user_id,
        location=request.location,
        status="Open"
    )

    try:
        db.add(new_sos)
        db.commit()
        db.refresh(new_sos)
        
        print(f"🚨 [SOS RECEIVED] User {request.user_id} is in DANGER!")
        print(f"📍 Location: {request.location}")
        
        return new_sos
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")