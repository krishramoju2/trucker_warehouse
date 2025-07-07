from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, database
from backend.models.user_model import UserCreate, UserLogin
from backend.auth.auth_handler import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    hashed_pw = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully."}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    token = create_access_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
