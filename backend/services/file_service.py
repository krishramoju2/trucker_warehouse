from sqlalchemy.orm import Session
from backend import models
from backend.utils import file_utils
from fastapi import UploadFile, HTTPException

def handle_upload(db: Session, file: UploadFile, uploaded_by: str):
    if not file_utils.is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    existing = db.query(models.File).filter(models.File.filename == file.filename).order_by(models.File.version.desc()).first()
    version = 1 if not existing else existing.version + 1

    path, saved_name = file_utils.save_upload_file(file)
    file_type = file.content_type

    new_file = models.File(
        filename=file.filename,
        file_type=file_type,
        path=path,
        uploaded_by=uploaded_by,
        version=version
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_file_by_id(db: Session, file_id: int):
    return db.query(models.File).filter(models.File.id == file_id).first()

def delete_file(db: Session, file_id: int):
    file_record = get_file_by_id(db, file_id)
    if file_record:
        import os
        if os.path.exists(file_record.path):
            os.remove(file_record.path)
        db.delete(file_record)
        db.commit()
        return True
    return False
