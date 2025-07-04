from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import database, models
from . import admin_router as router

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("/employees")
def view_employees(db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeInfo).all()

@router.get("/documents")
def view_documents(db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeDocuments).all()

@router.get("/employee/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == emp_id).first()

@router.get("/documents/{emp_id}")
def get_employee_documents(emp_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeDocuments).filter(models.EmployeeDocuments.employee_id == emp_id).first()

@router.delete("/employee/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(database.get_db)):
    obj = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == emp_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return {"deleted": True}
