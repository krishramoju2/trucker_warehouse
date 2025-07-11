from pydantic import BaseModel, constr, Field
from datetime import datetime

class FileCreate(BaseModel):
    filename: constr(min_length=3, max_length=255)
    file_type: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_\-/]+$')
    uploaded_by: constr(min_length=2, max_length=100)

class FileOut(BaseModel):
    id: int
    filename: constr(min_length=3, max_length=255)
    file_type: constr(min_length=3, max_length=50)
    path: constr(min_length=1)
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: constr(min_length=2, max_length=100)
    version: int = Field(ge=1)

    class Config:
        orm_mode = True
