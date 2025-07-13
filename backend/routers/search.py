from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict # Import Dict for the response model

# Assuming these imports are correct based on your project structure
from backend.utils.semantic_index import semantic_search
from backend.database import SessionLocal
from backend.schema_models import EmployeeInfo # This should be your SQLAlchemy model

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/semantic-search",
    response_model=List[Dict], # Changed response_model to List[Dict]
    summary="Perform a semantic search for employees",
    description="Searches for employees based on a natural language query using a semantic index and returns matching employee information."
)
def semantic_search_api(
    query: str,
    db: Session = Depends(get_db)
) -> List[Dict]: # Changed return type hint to List[Dict]
    """
    Performs a semantic search to find relevant employee IDs and then retrieves
    the full employee information from the database.

    Args:
        query: The natural language query string for semantic search.
        db: The database session dependency.

    Returns:
        A list of dictionaries, each representing an employee's information.
    """
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter cannot be empty."
        )

    try:
        emp_ids: List[str] = semantic_search(query) # Assuming semantic_search returns a list of IDs (e.g., strings or ints)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {e}"
        )

    if not emp_ids:
        return [] # Return an empty list if no IDs are found by semantic search

    # Fetch employee information from the database using the retrieved IDs
    # Assuming EmployeeInfo.id is the primary key and matches the type of emp_ids
    results = db.query(EmployeeInfo).filter(EmployeeInfo.id.in_(emp_ids)).all()

    # Convert SQLAlchemy ORM objects to dictionaries for the API response.
    # IMPORTANT: You MUST adjust the keys and attributes below to match
    # the actual column names/attributes of your 'EmployeeInfo' SQLAlchemy ORM model.
    employee_data = []
    for emp in results:
        # Example attributes. Replace with your actual EmployeeInfo model's attributes.
        employee_data.append({
            "id": emp.id,
            "name": emp.name if hasattr(emp, 'name') else None,
            "email": emp.email if hasattr(emp, 'email') else None,
            "department": emp.department if hasattr(emp, 'department') else None,
            # Add other relevant attributes from your EmployeeInfo ORM model here, e.g.:
            # "position": emp.position,
            # "hire_date": str(emp.hire_date), # Convert date objects to string
        })

    return employee_data
