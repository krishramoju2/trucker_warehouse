from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from backend import database, models
import shutil, os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/{employee_id}")
def upload_documents(
    employee_id: int,
    resume: UploadFile = File(...),
    educational_certificates: UploadFile = File(...),
    offer_letters: UploadFile = File(...),
    pan_card: UploadFile = File(...),
    aadhar_card: UploadFile = File(...),
    form_16_or_it_returns: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    def save(file: UploadFile):
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return path

    doc = models.EmployeeDocuments(
        employee_id=employee_id,
        resume=save(resume),
        educational_certificates=save(educational_certificates),
        offer_letters=save(offer_letters),
        pan_card=save(pan_card),
        aadhar_card=save(aadhar_card),
        form_16_or_it_returns=save(form_16_or_it_returns)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"status": "uploaded", "doc_id": doc.id}
