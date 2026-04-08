from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.missing_person import MissingPerson
from app.models.detection import Detection # استورد ده عشان الـ Count
from enum import Enum 
import shutil
import uuid
import os
from typing import List

# استيراد حماية الـ Token
from app.routers.sos_router import get_current_user 

router = APIRouter(prefix="/missing-persons", tags=["Missing Persons"])

class GenderChoices(str, Enum):
    male = "Male"
    female = "Female"

# 1. API البلاغ (تم تعديله عشان يسحب رقم اليوزر أوتوماتيك)
@router.post("/report")
def report_missing_person(
    name: str = Form(...),
    age: int = Form(...),
    gender: GenderChoices = Form(...), 
    location: str = Form(...),
    medical_notes: str = Form(None), 
    last_seen: str = Form(...), 
    image: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user) 
):
    file_ext = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"uploads/missing_persons/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    image_url = f"/static/missing_persons/{unique_filename}"

    new_report = MissingPerson(
        name=name,
        age=age,
        gender=gender.value, 
        location=location,
        medical_notes=medical_notes,
        last_seen=last_seen,
        image_url=image_url,
        reported_by=int(current_user_id) 
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {"message": "Report submitted successfully", "person_id": new_report.person_id}


@router.get("/my-reports")
def get_my_reports(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    reports = db.query(MissingPerson).filter(
        MissingPerson.reported_by == int(current_user_id)
    ).all()
    
    result = []
    for p in reports:
        
        det_count = db.query(Detection).filter(Detection.person_id == p.person_id).count()
        result.append({
            "person_id": p.person_id,
            "name": p.name,
            "status": p.status,
            "image_url": p.image_url,
            "detection_count": det_count
        })
    return result


@router.get("/all")
def get_all_missing_persons(db: Session = Depends(get_db)):
    return db.query(MissingPerson).order_by(MissingPerson.date_reported.desc()).all()