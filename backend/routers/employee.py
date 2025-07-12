from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from backend import database, models

router = APIRouter()


# -------------------------------
# 📦 Request and Response Schemas
# -------------------------------

class EmployeeCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    date_of_birth: str = Field(..., example="1990-05-15")
    address: str = Field(..., example="123 Main St, Springfield")
    contact_number: str = Field(..., example="9876543210")
    pan_number: str = Field(..., example="ABCDE1234F")
    aadhar_number: str = Field(..., example="123456789012")

class EmployeeOut(BaseModel):
    id: int
    name: str
    date_of_birth: str
    address: str
    contact_number: str
    pan_number: str
    aadhar_number: str

    class Config:
        orm_mode = True


# ---------------------
# 🚀 Endpoint: Create
# ---------------------
@router.post("/", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, db: Session = Depends(database.get_db)):
    try:
        dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    employee = models.EmployeeInfo(
        name=data.name,
        date_of_birth=dob,
        address=data.address,
        contact_number=data.contact_number,
        pan_number=data.pan_number,
        aadhar_number=data.aadhar_number,
    )

    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return employee


# ---------------------
# 📋 Endpoint: List All
# ---------------------
@router.get("/", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(database.get_db)):
    return db.query(models.EmployeeInfo).all()


# -------------------------------
# 🔍 Endpoint: Search by Name
# -------------------------------
@router.get("/search", response_model=list[EmployeeOut])
def search_employees(
    name: str = Query(..., min_length=1, example="john"),
    db: Session = Depends(database.get_db),
):
    employees = db.query(models.EmployeeInfo).filter(
        models.EmployeeInfo.name.ilike(f"%{name}%")
    ).all()
    return employees
