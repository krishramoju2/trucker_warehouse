from fastapi import APIRouter
from backend.utils.semantic_index import semantic_search
from backend.database import SessionLocal
from backend.schema_models import EmployeeInfo

router = APIRouter()

@router.get("/semantic-search")
def semantic_search_api(query: str):
    emp_ids = semantic_search(query)
    db = SessionLocal()
    results = db.query(EmployeeInfo).filter(EmployeeInfo.id.in_(emp_ids)).all()
    return results
