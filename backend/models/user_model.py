from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  # "admin" or "employee"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
