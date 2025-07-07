from pydantic import BaseModel, EmailStr, constr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    employee = "employee"

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=64, regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]+$')
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=64)
