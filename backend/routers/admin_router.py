from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import database, models # Assuming backend is your project root or a package

# No need for: from . import admin_router as router
# Just define the APIRouter directly

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("/employees")
def view_employees(db: Session = Depends(database.get_db)):
    """
    Retrieves all employee information.
    """
    return db.query(models.EmployeeInfo).all()

@router.get("/documents")
def view_documents(db: Session = Depends(database.get_db)):
    """
    Retrieves all employee documents information.
    """
    return db.query(models.EmployeeDocuments).all()

@router.get("/employee/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves details for a specific employee by ID.
    """
    employee = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/documents/{emp_id}")
def get_employee_documents(emp_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves documents for a specific employee by ID.
    """
    documents = db.query(models.EmployeeDocuments).filter(models.EmployeeDocuments.employee_id == emp_id).first()
    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documents not found for this employee")
    return documents

@router.delete("/employee/{emp_id}", status_code=status.HTTP_200_OK)
def delete_employee(emp_id: int, db: Session = Depends(database.get_db)):
    """
    Deletes an employee by ID.
    """
    obj = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == emp_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    db.delete(obj)
    db.commit()
    # Optionally, you might want to refresh the object to ensure it's detached from the session,
    # or simply return a success message.
    # db.refresh(obj) # Not needed if you are just returning a message.
    
    return {"message": f"Employee with ID {emp_id} deleted successfully"}
