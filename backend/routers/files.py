from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import file_service
from backend.models import file_model
from fastapi.responses import FileResponse

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload", response_model=file_model.FileOut)
def upload_file(file: UploadFile, uploaded_by: str, db: Session = Depends(get_db)):
    return file_service.handle_upload(db, file, uploaded_by)

@router.get("/{file_id}", response_model=file_model.FileOut)
def get_file_meta(file_id: int, db: Session = Depends(get_db)):
    file = file_service.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = file_service.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file.path, filename=file.filename)

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    if not file_service.delete_file(db, file_id):
        raise HTTPException(status_code=404, detail="File not found")
    return {"detail": "File deleted successfully"}
