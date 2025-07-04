from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend import database, models

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
    obj = models.EmployeeInfo(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/employee")
def list_employees(db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeInfo).all()
