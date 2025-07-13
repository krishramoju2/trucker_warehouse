# main.py (or your main FastAPI application file)
from fastapi import FastAPI
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend.routers import admin_router

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Authentication API",
    description="A simple API for user registration and authentication using FastAPI and SQLAlchemy.",
    version="1.0.0"
)

app.include_router(admin_router.router)

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the User Authentication API! Visit /docs for API documentation."}

# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL for simplicity. In production, you might use PostgreSQL, MySQL, etc.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # Needed for SQLite
)

# Create a declarative base for your ORM models
Base = declarative_base()

# Create a SessionLocal class to get database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# backend/models/user_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
from typing import Optional

# SQLAlchemy Base imported from database.py
# For this self-contained example, we'll redefine it here for clarity,
# but in a real project, you'd import Base from backend.database
Base = declarative_base()

# SQLAlchemy ORM Model
class User(Base):
    """
    SQLAlchemy ORM model for the 'users' table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False) # e.g., "user", "admin"

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

# Pydantic Models for request and response validation/serialization
class UserBase(BaseModel):
    """
    Base Pydantic model for user data.
    """
    email: EmailStr
    role: Optional[str] = "user"

    class Config:
        from_attributes = True # Changed from orm_mode for Pydantic v2

class UserCreate(UserBase):
    """
    Pydantic model for user creation (includes password).
    """
    password: str

class UserLogin(BaseModel):
    """
    Pydantic model for user login (email and password).
    """
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """
    Pydantic model for user response (excludes hashed password).
    """
    id: int


# backend/auth/auth_handler.py
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Import the SQLAlchemy User model and get_db dependency
from backend.models.user_model import User
from backend.database import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
# IMPORTANT: Replace with a strong, randomly generated secret key in production!
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-replace-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTPException if the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # You can also get the role from the payload if needed for authorization
        # role: str = payload.get("role")
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# backend/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import database # Assuming database includes your get_db function
from backend.models.user_model import UserCreate, UserLogin, User, UserResponse # Import all necessary models

# Assuming your SQLAlchemy User model is defined in backend.models.user_model
# and is named 'User'. If it's named differently, please adjust 'User' above.

from backend.auth.auth_handler import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    response_model=UserResponse, # Specify response model for automatic serialization
    status_code=status.HTTP_201_CREATED, # Standard status code for successful creation
    summary="Register a new user",
    description="Registers a new user with email, password, and an optional role. Returns the created user's details."
)
def signup(user: UserCreate, db: Session = Depends(database.get_db)):
    """
    Handles user registration by creating a new user in the database.
    - Checks if the email is already registered.
    - Hashes the provided password before storing.
    - Assigns a default role ('user') if not specified.
    """
    # Use the directly imported User model
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pw = hash_password(user.password)
    # Use the directly imported User model
    new_user = User(email=user.email, hashed_password=hashed_pw, role=user.role)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user) # Refresh to get the generated ID and any default values
    except Exception as e:
        db.rollback() # Rollback in case of an error during commit
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during user creation: {e}"
        )

    return new_user # FastAPI will automatically convert this SQLAlchemy model to UserResponse due to response_model

@router.post(
    "/login",
    summary="Authenticate user and get access token",
    description="Authenticates a user with email and password. Returns an access token upon successful login."
)
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    """
    Authenticates a user and generates a JWT access token.
    - Verifies email and password against stored credentials.
    - Returns an access token for subsequent authenticated requests.
    """
    # Use the directly imported User model
    db_user = db.query(User).filter(User.email == user.email).first()

    # Check if user exists and password is correct
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"}, # Standard header for auth failures
        )

    # Create the access token
    # You can customize token expiration (e.g., timedelta(minutes=60))
    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})

    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse, # Specify response model
    summary="Get current authenticated user info",
    description="Retrieves the details of the currently authenticated user based on the provided JWT."
)
def get_current_user_info(current_user: User = Depends(get_current_user)): # Use the get_current_user dependency
    """
    Retrieves information about the currently authenticated user.
    This route requires a valid JWT in the Authorization header (Bearer token).
    """
    return current_user

@router.get(
    "/admin-status",
    summary="Check admin status (admin-only access)",
    description="An example route that only users with 'admin' role can access."
)
def check_admin_status(current_user: User = Depends(get_current_user)): # Use the get_current_user dependency
    """
    Demonstrates a route accessible only by users with the 'admin' role.
    If the authenticated user is not an admin, a 403 Forbidden error is returned.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required."
        )
    return {"message": f"Welcome, admin {current_user.email}! You have access to administrative features."}
