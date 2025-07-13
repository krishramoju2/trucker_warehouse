# trucker_warehouse/backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# Assuming database includes your get_db function
from backend import database

# Import only the necessary models from your user_model file.
# We will use UserRole as the SQLAlchemy ORM model, and UserCreate/UserLogin for Pydantic input.
# As per your instruction, we are avoiding 'User' and 'UserResponse'.
from backend.models.user_model import UserCreate, UserLogin, UserRole # UserRole is the SQLAlchemy ORM model

# Assuming your authentication logic is here
from backend.auth.auth_handler import verify_password, hash_password, create_access_token, get_current_user

# --- Pydantic Model for API Response ---
# Since you want to avoid 'UserResponse' and expose only 'email' and 'role',
# we define a simple Pydantic model here to shape the output.
class UserOut(BaseModel):
    email: EmailStr
    role: str

    class Config:
        # Enable ORM mode to allow direct conversion from SQLAlchemy UserRole model to this Pydantic model
        orm_mode = True

# --- FastAPI Router Definition ---
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    response_model=UserOut, # Specify UserOut as the response model
    status_code=status.HTTP_201_CREATED, # Standard status code for successful creation
    summary="Register a new user",
    description="Registers a new user with email, password, and an optional role. Returns the created user's details (email and role)."
)
def signup(user: UserCreate, db: Session = Depends(database.get_db)):
    """
    Handles user registration by creating a new user in the database.
    - Checks if the email is already registered using the UserRole ORM model.
    - Hashes the provided password before storing.
    - Assigns a default role ('user') if not specified in UserCreate.
    - Returns the created user's email and role.
    """
    # Use the imported UserRole ORM model for database queries
    existing_user = db.query(UserRole).filter(UserRole.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pw = hash_password(user.password)
    # Create a new UserRole instance using data from UserCreate
    new_user = UserRole(email=user.email, hashed_password=hashed_pw, role=user.role)

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

    # FastAPI will automatically convert this UserRole ORM model to UserOut due to response_model
    return new_user

@router.post(
    "/login",
    summary="Authenticate user and get access token",
    description="Authenticates a user with email and password. Returns an access token upon successful login."
)
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    """
    Authenticates a user and generates a JWT access token.
    - Verifies email and password against stored credentials using the UserRole ORM model.
    - Returns an access token for subsequent authenticated requests.
    """
    # Use the imported UserRole ORM model for database queries
    db_user = db.query(UserRole).filter(UserRole.email == user.email).first()

    # Check if user exists and password is correct
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"}, # Standard header for auth failures
        )

    # Create the access token using data from the authenticated UserRole object
    # The 'sub' claim will be the user's email, and 'role' will be their role.
    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})

    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserOut, # Specify UserOut as the response model
    summary="Get current authenticated user info",
    description="Retrieves the details (email and role) of the currently authenticated user based on the provided JWT."
)
# The get_current_user dependency is assumed to return a dictionary
# containing 'email' and 'role' for the authenticated user.
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Retrieves information about the currently authenticated user.
    This route requires a valid JWT in the Authorization header (Bearer token).
    """
    # Convert the dictionary returned by get_current_user into a UserOut Pydantic model
    return UserOut(**current_user)

@router.get(
    "/admin-status",
    summary="Check admin status (admin-only access)",
    description="An example route that only users with 'admin' role can access."
)
# The get_current_user dependency is assumed to return a dictionary
# containing 'email' and 'role' for the authenticated user.
def check_admin_status(current_user: dict = Depends(get_current_user)):
    """
    Demonstrates a route accessible only by users with the 'admin' role.
    If the authenticated user is not an admin, a 403 Forbidden error is returned.
    """
    # Access the 'role' from the dictionary returned by get_current_user
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required."
        )
    return {"message": f"Welcome, admin {current_user.get('email')}! You have access to administrative features."}
