from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import file_service
from backend.models import file_model
from backend.utils.virus_scan import scan_file
from fastapi.responses import FileResponse
import shutil
import os
import uuid

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = "uploads"

@router.post("/upload", response_model=file_model.FileOut)
def upload_file(file: UploadFile, uploaded_by: str, db: Session = Depends(get_db)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    is_clean = scan_file(file_path)
    if not is_clean:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Virus detected in uploaded file")

    return file_service.handle_upload(db, file_path, file.filename, uploaded_by)

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
