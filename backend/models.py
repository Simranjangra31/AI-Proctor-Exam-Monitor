from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class IDRecord(Base):
    __tablename__ = "id_records"

    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String, index=True)
    confidence = Column(Float)
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String, unique=True, index=True)
    name = Column(String)
    reference_photo_path = Column(String)
    face_embedding = Column(String)  # Stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class ProctoringAlert(Base):
    __tablename__ = "proctoring_alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_prn = Column(String, index=True)
    alert_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
