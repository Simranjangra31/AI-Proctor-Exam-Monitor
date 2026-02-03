from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
from pipeline.pipeline import run_pipeline
# We lazy load face_utils inside endpoints to save memory on start
from database import SessionLocal
from models import IDRecord, Student, ProctoringAlert
from pydantic import BaseModel
import json

class AlertData(BaseModel):
    prn: str
    type: str
    description: str

app = FastAPI()
print("MAIN.PY LOADED SUCCESSFULLY - CHECKING ROUTES")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/exam")
async def read_exam():
    return FileResponse("static/exam.html")

UPLOAD_DIR = "uploads"
REF_DIR = "uploads/references"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)

@app.post("/detect-id")
async def detect_id(file: UploadFile = File(...)):
    image_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run pipeline
    result = run_pipeline(image_path)
    if result.get("status") == "error":
        return result

    prn = result.get("prn")
    confidence = result.get("confidence")
    photo_path = result.get("photo_path")
    
    # 🔹 Verify PRN against database
    db = SessionLocal()
    student_record = None
    
    try:
        # Save ID record
        record = IDRecord(
            prn=prn,
            confidence=confidence,
            image_path=image_path
        )
        db.add(record)
        
        # Verify Student
        student = db.query(Student).filter(Student.prn == prn).first()
        if student:
            student_record = {
                "id": student.id,
                "name": student.name,
                "verified": True
            }
        
        db.commit()
    finally:
        db.close()

    return {
        "status": "success",
        "data": {
            "prn": prn,
            "confidence": confidence,
            "verified_student": student_record
        }
    }

@app.post("/save-reference")
async def save_reference(file: UploadFile = File(...), prn: str = Form(...)):
    # Save the student's proctoring reference photo
    ref_path = os.path.join(REF_DIR, f"{prn}_ref.jpg")
    with open(ref_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"status": "success", "message": "Reference photo saved."}

@app.post("/verify-proctored-face")
async def verify_proctored_face(file: UploadFile = File(...), prn: str = Form(...)):
    # Compare live proctoring frame against the reference photo saved in /save-reference
    ref_path = os.path.join(REF_DIR, f"{prn}_ref.jpg")
    
    if not os.path.exists(ref_path):
        return {"status": "error", "message": "Reference photo not found."}

    live_capture_path = os.path.join(UPLOAD_DIR, f"live_{prn}.jpg")
    with open(live_capture_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        from pipeline.face_utils import analyze_proctoring_frame
        status, detail = analyze_proctoring_frame(live_capture_path, ref_path)
        
        return {
            "status": "success",
            "data": {
                "verdict": status, # SUCCESS, NO_FACE, MULTI_FACE, MISMATCH, ERROR
                "distance": float(detail) if isinstance(detail, (int, float)) else None
            }
        }
    except Exception as e:
        print(f"Proctoring Face Verification Endpoint Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/log-alert")
async def log_alert(data: AlertData):
    db = SessionLocal()
    try:
        alert = ProctoringAlert(
            student_prn=data.prn,
            alert_type=data.type,
            description=data.description
        )
        db.add(alert)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
