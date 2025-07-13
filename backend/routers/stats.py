from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict # For the response model

# Assuming these imports are correct based on your project structure
from backend.database import get_db
# You need to import your SQLAlchemy models. It's common to have a single 'models' module
# or import them individually if structured differently.
# For example, if your models are defined in backend/models/user_model.py and backend/models/employee_model.py
# you might need to import them like this:
from backend.models import user_model # This seems to be for UserCreate, UserLogin, not EmployeeInfo or EmployeeDocuments
from backend.models import employee_model # Assuming your EmployeeInfo and EmployeeDocuments are here

# --- Pydantic Models for Responses ---
# It's good practice to define Pydantic models for your API responses.
# This helps with automatic serialization and OpenAPI documentation.
class CountResponse(BaseModel):
    count: int

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get(
    "/employees",
    response_model=CountResponse, # Specify the Pydantic response model
    summary="Get Employee Count",
    description="Returns the total number of employee records in the database."
)
def get_employee_count(db: Session = Depends(get_db)) -> Dict[str, int]:
    """
    Retrieves the total count of employees from the EmployeeInfo table.

    Args:
        db: The database session dependency.

    Returns:
        A dictionary containing the count of employees.
    """
    # Ensure 'employee_model.EmployeeInfo' is the correct path to your SQLAlchemy model
    count = db.query(employee_model.EmployeeInfo).count()
    return {"count": count}

@router.get(
    "/documents",
    response_model=CountResponse, # Specify the Pydantic response model
    summary="Get Document Count",
    description="Returns the total number of employee document records in the database."
)
def get_document_count(db: Session = Depends(get_db)) -> Dict[str, int]:
    """
    Retrieves the total count of employee documents from the EmployeeDocuments table.

    Args:
        db: The database session dependency.

    Returns:
        A dictionary containing the count of documents.
    """
    # Ensure 'employee_model.EmployeeDocuments' is the correct path to your SQLAlchemy model
    count = db.query(employee_model.EmployeeDocuments).count()
    return {"count": count}
