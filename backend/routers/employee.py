from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend import database, models
from fastapi import Query
from datetime import datetime

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    date_of_birth: str
    address: str
    contact_number: str
    pan_number: str
    aadhar_number: str

@router.post("/employee")
def create_employee(data: EmployeeCreate, db: Session = Depends(database.get_db)):
    # Convert string to date object
    dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()

    obj = models.EmployeeInfo(
        name=data.name,
        date_of_birth=dob,
        address=data.address,
        contact_number=data.contact_number,
        pan_number=data.pan_number,
        aadhar_number=data.aadhar_number,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee")
def list_employees(db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeInfo).all()
@router.get("/employee/search")
def search_employees(name: str = Query(..., min_length=1), db: Session = Depends(database.get_db):
    results = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.name.ilike(f"%{name}%")).all()
    return results
