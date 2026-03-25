from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.detection import Detection
from app.models.missing_person import MissingPerson
import shutil
import uuid
import os
from sqlalchemy.orm import Session

router = APIRouter(prefix="/detections", tags=["AI Detections"])

@router.post("/match")
def register_ai_detection(
    person_id: int = Form(...), 
    confidence_level: float = Form(...), 
    location: str = Form(...), 
    camera_id: int = Form(None), 
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
   
    file_ext = image.filename.split(".")[-1]
    unique_filename = f"ai_match_{uuid.uuid4()}.{file_ext}"
    file_path = f"uploads/detections/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    image_url = f"/static/detections/{unique_filename}"

   
    new_detection = Detection(
        person_id=person_id,
        camera_id=camera_id,
        confidence_level=confidence_level,
        detected_image_url=image_url,
        location=location
    )
    
    db.add(new_detection)
    db.commit()
    db.refresh(new_detection)

    return {
        "message": "AI Match recorded successfully!",
        "detection_id": new_detection.detection_id,
        "person_id": person_id
    }

@router.get("/notifications/{user_id}")
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
   
    notifications = db.query(Detection, MissingPerson.name)\
        .join(MissingPerson, Detection.person_id == MissingPerson.person_id)\
        .filter(MissingPerson.reported_by == user_id)\
        .order_by(Detection.detected_at.desc())\
        .all()
    
    
    result = []
    for det, person_name in notifications:
        result.append({
            "detection_id": det.detection_id,
            "person_id": det.person_id,
            "person_name": person_name, 
            "confidence_level": det.confidence_level, 
            "location": det.location, 
            "detected_image_url": det.detected_image_url, 
            "detected_at": det.detected_at 
        })
        
    return result