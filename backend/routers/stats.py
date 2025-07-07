from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import models

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/employees")
def get_employee_count(db: Session = Depends(get_db)):
    count = db.query(models.EmployeeInfo).count()
    return {"count": count}

@router.get("/documents")
def get_document_count(db: Session = Depends(get_db)):
    count = db.query(models.EmployeeDocuments).count()
    return {"count": count}
