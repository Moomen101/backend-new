from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database import Base
from datetime import datetime

class Detection(Base):
    __tablename__ = "detections"

    detection_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("missing_persons.person_id"))
    camera_id = Column(Integer, ForeignKey("cameras.camera_id"), nullable=True)
    confidence_level = Column(Float)
    detected_image_url = Column(String(255))
    detected_at = Column(DateTime, default=datetime.utcnow)
    location = Column(String(255))