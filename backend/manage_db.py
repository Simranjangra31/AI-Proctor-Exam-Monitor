from database import SessionLocal, engine, Base
from models import Student
import sys

def list_students():
    db = SessionLocal()
    students = db.query(Student).all()
    print("\n--- Registered Students ---")
    if not students:
        print("No students found in database.")
    for s in students:
        print(f"PRN: {s.prn} | Name: {s.name}")
    print("---------------------------\n")
    db.close()

def add_student(prn, name):
    db = SessionLocal()
    existing = db.query(Student).filter(Student.prn == prn).first()
    if existing:
        print(f"Error: Student with PRN {prn} already exists.")
    else:
        new_student = Student(prn=prn, name=name)
        db.add(new_student)
        db.commit()
        print(f"Successfully added {name} (PRN: {prn})")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_db.py list")
        print("  python manage_db.py add <PRN> <NAME>")
    elif sys.argv[1] == "list":
        list_students()
    elif sys.argv[1] == "add" and len(sys.argv) >= 4:
        add_student(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        print("Invalid command.")
