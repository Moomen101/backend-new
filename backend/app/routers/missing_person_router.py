from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.missing_person import MissingPerson
from enum import Enum  
import shutil
import uuid
import os

router = APIRouter(prefix="/missing-persons", tags=["Missing Persons"])


class GenderChoices(str, Enum):
    male = "Male"
    female = "Female"

@router.post("/report")
def report_missing_person(
    name: str = Form(...),
    age: int = Form(...),
   
    gender: GenderChoices = Form(...), 
    location: str = Form(...),
    medical_notes: str = Form(None), 
    last_seen: str = Form(...), 
    reported_by: int = Form(...),
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)
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
        reported_by=reported_by
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Report submitted successfully",
        "person_id": new_report.person_id,
        "image_url": image_url
    }
  
    db.refresh(new_report)

    return {
        "message": "Report submitted successfully",
        "person_id": new_report.person_id,
        "image_url": image_url
    }


@router.get("/all")
def get_all_missing_persons(db: Session = Depends(get_db)):
    
    reports = db.query(MissingPerson).order_by(MissingPerson.date_reported.desc()).all()
    return reports