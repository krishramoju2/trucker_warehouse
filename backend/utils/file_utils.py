import os
from uuid import uuid4
from fastapi import UploadFile
from typing import Tuple

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg", "zip"}
UPLOAD_DIR = "uploaded_files"

def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file: UploadFile, subdir: str = "") -> Tuple[str, str]:
    os.makedirs(os.path.join(UPLOAD_DIR, subdir), exist_ok=True)
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid4().hex}.{ext}"
    full_path = os.path.join(UPLOAD_DIR, subdir, unique_name)

    with open(full_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return full_path, unique_name
