from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from backend.schema_models import EmployeeInfo 
from backend import database, models

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    dob: str
    address: str
    contact: str
    pan: str
    aadhar: str

class EmployeeUpdate(BaseModel):
    name: str | None = None
    dob: str | None = None
    address: str | None = None
    contact: str | None = None
    pan: str | None = None
    aadhar: str | None = None

def serialize_employee(emp: EmployeeInfo) -> dict:
    return {
        
        "Trucker Name": emp.name,
        "date_of_birth": emp.dob.isoformat() if emp.dob else None,
        "Home Address": emp.address,
        "contact_number": emp.contact,
        "Driving License Number": emp.pan,
        "aadhar_number": emp.aadhar,
    }

@router.post("/", response_model=dict)
def create_employee(data: EmployeeCreate, db: Session = Depends(database.get_db)):
    dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    obj = models.EmployeeInfo(
        name=data.name,
        date_of_birth=dob,
        address=data.address,
        contact_number=data.contact,
        pan_number=data.pan,
        aadhar_number=data.aadhar,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    try:
        return {"message": "Employee created", "id": obj.id}
    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=list)
def list_employees(db: Session = Depends(database.get_db)):
    employees = db.query(models.EmployeeInfo).all()
    return [serialize_employee(emp) for emp in employees]

@router.get("/{employee_id}", response_model=dict)
def get_employee(employee_id: int, db: Session = Depends(database.get_db)):
    emp = db.query(EmployeeInfo).filter(EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return serialize_employee(emp)

@router.put("/{employee_id}", response_model=dict)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(database.get_db)):
    emp = db.query(EmployeeInfo).filter(EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if data.name is not None:
        emp.name = data.name
    if data.date_of_birth is not None:
        emp.date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    if data.address is not None:
        emp.address = data.address
    if data.contact is not None:
        emp.contact = data.contact
    if data.pan_number is not None:
        emp.pan = data.pan
    if data.aadhar is not None:
        emp.aadhar = data

    db.commit()
    db.refresh(emp)
    return {"message": "Employee updated", "id": emp.id}

@router.delete("/{employee_id}", response_model=dict)
def delete_employee(employee_id: int, db: Session = Depends(database.get_db)):
    emp = db.query(EmployeeInfo).filter(EmployeeInfo.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted", "id": employee_id}

@router.get("/search/")
def search_employees(name: str = Query(..., min_length=1), db: Session = Depends(database.get_db)):
    results = db.query(EmployeeInfo).filter(EmployeeInfo.name.ilike(f"%{name}%")).all()
    return [serialize_employee(emp) for emp in results]

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

app = FastAPI()
app.include_router(router, prefix="/employee", tags=["Employee"])

# 👇 Mount frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 👇 HTML page routes (register.html, view.html, upload.html, dashboard.html, search.html)
@app.get("/", response_class=HTMLResponse)
def index():
    with open("frontend/register.html") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
def register():
    with open("frontend/register.html") as f:
        return f.read()

@app.get("/employees", response_class=HTMLResponse)
def list_view():
    with open("frontend/view.html") as f:
        return f.read()

@app.get("/upload", response_class=HTMLResponse)
def upload():
    with open("frontend/upload.html") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("frontend/dashboard.html") as f:
        return f.read()

@app.get("/search", response_class=HTMLResponse)
def search():
    with open("frontend/search.html") as f:
        return f.read()

