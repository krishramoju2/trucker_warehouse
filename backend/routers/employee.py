from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime, date

# Assuming 'backend' is your project root and contains database.py and models.py
# Make sure your import paths are correct relative to where this file will be located
from backend import database, models

router = APIRouter(
    prefix="/employees", # All routes under this router will be prefixed with /employees
    tags=["Employees"], # Groups the routes in the OpenAPI documentation
)

# -------------------------------
# 📦 Request and Response Schemas
# -------------------------------

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John Doe")
    date_of_birth: date = Field(..., example="1990-05-15") # Using date type directly
    address: str = Field(..., min_length=5, max_length=200, example="123 Main St, Springfield")
    contact_number: str = Field(..., pattern=r"^\d{10}$", example="9876543210") # Simple 10-digit validation
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", example="ABCDE1234F")
    aadhar_number: str = Field(..., pattern=r"^\d{12}$", example="123456789012")

class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    pass

class EmployeeUpdate(EmployeeBase):
    """Schema for updating an existing employee. All fields are optional for partial updates."""
    name: str | None = Field(None, min_length=2, max_length=100, example="Jane Smith")
    date_of_birth: date | None = Field(None, example="1992-08-20")
    address: str | None = Field(None, min_length=5, max_length=200, example="456 Oak Ave, Capital City")
    contact_number: str | None = Field(None, pattern=r"^\d{10}$", example="1234567890")
    pan_number: str | None = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", example="FGHIJ5678K")
    aadhar_number: str | None = Field(None, pattern=r"^\d{12}$", example="987654321098")


class EmployeeOut(EmployeeBase):
    """Schema for returning employee data."""
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True

# -------------------------------
# 🚀 Dependency
# -------------------------------

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# ⚡ Employee Endpoints (CRUD Operations)
# -------------------------------

# ---------------------
# 🚀 Endpoint: Create Employee
# ---------------------
@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Creates a new employee record.
    """
    db_employee = models.EmployeeInfo(**data.model_dump())
    db_employee.created_at = datetime.now() # Set creation timestamp
    db_employee.updated_at = datetime.now() # Initialize updated_at on creation

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}"
        )
    return db_employee

# ---------------------
# 📋 Endpoint: List All Employees
# ---------------------
@router.get("/", response_model=list[EmployeeOut])
def list_employees(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of all employees with optional pagination.
    """
    employees = db.query(models.EmployeeInfo).offset(skip).limit(limit).all()
    return employees

# ---------------------
# 🔍 Endpoint: Get Employee by ID
# ---------------------
@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single employee record by its ID.
    """
    employee = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

# ---------------------
# ✏️ Endpoint: Update Employee
# ---------------------
@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing employee record by ID.
    """
    db_employee = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Update only the provided fields
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_employee, field, value)

    db_employee.updated_at = datetime.now() # Set update timestamp

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update employee: {str(e)}"
        )
    return db_employee

# ---------------------
# 🗑️ Endpoint: Delete Employee
# ---------------------
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Deletes an employee record by ID.
    """
    db_employee = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    try:
        db.delete(db_employee)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete employee: {str(e)}"
        )
    return # No content returned for 204

# -------------------------------
# 🔍 Endpoint: Search by Name
# -------------------------------
@router.get("/search", response_model=list[EmployeeOut])
def search_employees(
    name: str = Query(..., min_length=1, example="john"),
    db: Session = Depends(get_db),
):
    """
    Searches for employees by name (case-insensitive, partial match).
    """
    employees = db.query(models.EmployeeInfo).filter(
        models.EmployeeInfo.name.ilike(f"%{name}%")
    ).all()
    return employees
