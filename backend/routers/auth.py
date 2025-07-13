from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import models, database # Assuming models includes your SQLAlchemy User model
from backend.models.user_model import UserCreate, UserLogin # Pydantic models for request/response
from backend.auth.auth_handler import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup", 
    response_model=UserResponse, # Ensure the response matches the Pydantic model
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
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered."
        )
    
    hashed_pw = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw, role=user.role)
    
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
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
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

# Example of a protected route using get_current_user dependency
@router.get(
    "/me", 
    response_model=UserResponse, 
    summary="Get current authenticated user info",
    description="Retrieves the details of the currently authenticated user based on the provided JWT."
)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """
    Retrieves information about the currently authenticated user.
    This route requires a valid JWT in the Authorization header (Bearer token).
    """
    return current_user

# Example of a protected route requiring a specific role
@router.get(
    "/admin-status", 
    summary="Check admin status (admin-only access)",
    description="An example route that only users with 'admin' role can access."
)
def check_admin_status(current_user: models.User = Depends(get_current_user)):
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
