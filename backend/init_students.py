from database import SessionLocal, engine, Base
from models import Student
import json

def init_students():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if test student exists
    test_prn = "1234567890"
    existing = db.query(Student).filter(Student.prn == test_prn).first()
    
    if not existing:
        student = Student(
            prn=test_prn,
            name="Test Student",
            reference_photo_path="data/test_student.jpg",
            face_embedding=json.dumps([0.1]*128) # Placeholder
        )
        db.add(student)
        db.commit()
        print(f"Added test student: {test_prn}")
    else:
        print("Test student already exists")
    
    db.close()

if __name__ == "__main__":
    init_students()
