from pydantic import BaseModel
from datetime import datetime

class FileCreate(BaseModel):
    filename: str
    file_type: str
    uploaded_by: str

class FileOut(BaseModel):
    id: int
    filename: str
    file_type: str
    path: str
    upload_time: datetime
    uploaded_by: str
    version: int

    class Config:
        orm_mode = True
