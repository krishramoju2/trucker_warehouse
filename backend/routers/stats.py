from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict # For the response model

# Assuming these imports are correct based on your project structure
from backend.database import get_db

# IMPORTANT: Based on your instructions, the SQLAlchemy ORM models
# EmployeeInfo and EmployeeDocuments are now assumed to be available
# directly from the 'backend.database' module.
# If your ORM models are located elsewhere, you MUST adjust these imports
# to their correct path within your project.
from backend.database import EmployeeInfo, EmployeeDocuments

from backend.models import user_model # This module remains as per your instruction

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
    # Using EmployeeInfo directly, assuming it's imported from backend.database
    count = db.query(EmployeeInfo).count()
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
    # Using EmployeeDocuments directly, assuming it's imported from backend.database
    count = db.query(EmployeeDocuments).count()
    return {"count": count}
