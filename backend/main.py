from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from backend import database, models

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    date_of_birth: str
    address: str
    contact_number: str
    pan_number: str
    aadhar_number: str

class EmployeeUpdate(BaseModel):
    name: str | None = None
    date_of_birth: str | None = None
    address: str | None = None
    contact_number: str | None = None
    pan_number: str | None = None
    aadhar_number: str | None = None

def serialize_employee(emp: schema_models.EmployeeInfo) -> dict:
    return {
        "id": emp.id,
        "name": emp.name,
        "date_of_birth": emp.date_of_birth.isoformat() if emp.date_of_birth else None,
        "address": emp.address,
        "contact_number": emp.contact_number,
        "pan_number": emp.pan_number,
        "aadhar_number": emp.aadhar_number,
    }

@router.post("/", response_model=dict)
def create_employee(data: EmployeeCreate, db: Session = Depends(database.get_db)):
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
    return {"message": "Employee created", "id": obj.id}

@router.get("/", response_model=list)
def list_employees(db: Session = Depends(database.get_db)):
    employees = db.query(models.EmployeeInfo).all()
    return [serialize_employee(emp) for emp in employees]

@router.get("/{employee_id}", response_model=dict)
def get_employee(employee_id: int, db: Session = Depends(database.get_db)):
    emp = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return serialize_employee(emp)

@router.put("/{employee_id}", response_model=dict)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(database.get_db)):
    emp = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if data.name is not None:
        emp.name = data.name
    if data.date_of_birth is not None:
        emp.date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    if data.address is not None:
        emp.address = data.address
    if data.contact_number is not None:
        emp.contact_number = data.contact_number
    if data.pan_number is not None:
        emp.pan_number = data.pan_number
    if data.aadhar_number is not None:
        emp.aadhar_number = data.aadhar_number

    db.commit()
    db.refresh(emp)
    return {"message": "Employee updated", "id": emp.id}

@router.delete("/{employee_id}", response_model=dict)
def delete_employee(employee_id: int, db: Session = Depends(database.get_db)):
    emp = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted", "id": employee_id}

@router.get("/search/")
def search_employees(name: str = Query(..., min_length=1), db: Session = Depends(database.get_db)):
    results = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.name.ilike(f"%{name}%")).all()
    return [serialize_employee(emp) for emp in results]

