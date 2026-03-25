from sqlalchemy import Column, Integer, String
from app.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    location = Column(String(255))
    rtsp_url = Column(String(255), nullable=True)
    status = Column(String(50), default="Active")