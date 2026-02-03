from database import SessionLocal
from models import IDRecord

db = SessionLocal()

records = db.query(IDRecord).all()
for r in records:
    print(r.id, r.prn, r.confidence, r.image_path, r.created_at)

db.close()
