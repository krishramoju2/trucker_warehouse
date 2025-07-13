from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
import shutil
import os
from datetime import datetime

# Assuming 'backend' is your project root and contains database.py and models.py
# Make sure your import paths are correct relative to where this file will be located
from backend import database, models

router = APIRouter(
    prefix="/documents",  # All routes under this router will be prefixed with /documents
    tags=["Employee Documents"], # Groups the routes in the OpenAPI documentation
)

# --- Configuration ---
UPLOAD_DIR = "uploads"
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Request and Response Schemas ---

class DocumentBase(BaseModel):
    # These fields will store the paths to the uploaded files
    resume: str | None = None
    educational_certificates: str | None = None
    offer_letters: str | None = None
    pan_card: str | None = None
    aadhar_card: str | None = None
    form_16_or_it_returns: str | None = None

class DocumentOut(DocumentBase):
    id: int
    employee_id: int
    uploaded_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True # This tells Pydantic to read data from SQLAlchemy models

# --- Dependency ---

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Function for File Saving ---

def save_uploaded_file(file: UploadFile, employee_id: int) -> str:
    """
    Saves an uploaded file to the UPLOAD_DIR within a subdirectory for the employee.
    Returns the relative path to the saved file.
    """
    # Create a unique subdirectory for each employee's documents
    employee_upload_dir = os.path.join(UPLOAD_DIR, str(employee_id))
    os.makedirs(employee_upload_dir, exist_ok=True)

    # Sanitize filename to prevent directory traversal attacks
    filename = os.path.basename(file.filename)
    # Optional: Add a UUID to filename to prevent collisions for same filename uploads
    # import uuid
    # file_extension = os.path.splitext(filename)[1]
    # unique_filename = f"{uuid.uuid4()}{file_extension}"
    # file_path = os.path.join(employee_upload_dir, unique_filename)

    file_path = os.path.join(employee_upload_dir, filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file '{filename}': {str(e)}"
        )
    return file_path # Return the full path relative to the server root for storage

# --- CRUD Endpoints ---

# ---------------------
# 🚀 Endpoint: Upload (Create) Documents
# ---------------------
@router.post("/{employee_id}", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_employee_documents(
    employee_id: int,
    resume: UploadFile = File(None, description="Employee's resume"), # Made optional
    educational_certificates: UploadFile = File(None, description="Educational certificates"),
    offer_letters: UploadFile = File(None, description="Offer letters from previous employers"),
    pan_card: UploadFile = File(None, description="PAN Card copy"),
    aadhar_card: UploadFile = File(None, description="Aadhar Card copy"),
    form_16_or_it_returns: UploadFile = File(None, description="Form 16 or Income Tax Returns"),
    db: Session = Depends(get_db)
):
    """
    Uploads multiple documents for a specific employee.
    If documents for the employee already exist, they will be updated/overwritten.
    """
    # Check if employee exists
    employee = db.query(models.EmployeeInfo).filter(models.EmployeeInfo.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found."
        )

    # Check if a document record already exists for this employee
    db_documents = db.query(models.EmployeeDocuments).filter(
        models.EmployeeDocuments.employee_id == employee_id
    ).first()

    if not db_documents:
        # Create a new document entry if none exists
        db_documents = models.EmployeeDocuments(employee_id=employee_id)
        db_documents.uploaded_at = datetime.now()
    
    db_documents.updated_at = datetime.now() # Always update timestamp on file upload/update

    # Dictionary to map schema fields to uploaded files
    files_to_process = {
        "resume": resume,
        "educational_certificates": educational_certificates,
        "offer_letters": offer_letters,
        "pan_card": pan_card,
        "aadhar_card": aadhar_card,
        "form_16_or_it_returns": form_16_or_it_returns,
    }

    # Process each uploaded file
    for doc_field, uploaded_file in files_to_process.items():
        if uploaded_file and uploaded_file.filename: # Ensure a file was actually provided
            try:
                file_path = save_uploaded_file(uploaded_file, employee_id)
                setattr(db_documents, doc_field, file_path) # Store the path in the database
            except HTTPException as e:
                # Re-raise HTTPExceptions from save_uploaded_file
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing {doc_field}: {str(e)}"
                )

    try:
        db.add(db_documents)
        db.commit()
        db.refresh(db_documents)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document entry already exists for this employee, use PUT to update."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document record: {str(e)}"
        )
    return db_documents

# ---------------------
# 📋 Endpoint: Get Documents by Employee ID
# ---------------------
@router.get("/{employee_id}", response_model=DocumentOut)
def get_employee_documents(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieves document paths for a specific employee.
    """
    documents = db.query(models.EmployeeDocuments).filter(
        models.EmployeeDocuments.employee_id == employee_id
    ).first()
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for employee ID {employee_id} not found."
        )
    return documents

# ---------------------
# ✏️ Endpoint: Update Documents (Partial Upload)
# ---------------------
@router.put("/{employee_id}", response_model=DocumentOut)
def update_employee_documents(
    employee_id: int,
    resume: UploadFile = File(None, description="Employee's resume"),
    educational_certificates: UploadFile = File(None, description="Educational certificates"),
    offer_letters: UploadFile = File(None, description="Offer letters from previous employers"),
    pan_card: UploadFile = File(None, description="PAN Card copy"),
    aadhar_card: UploadFile = File(None, description="Aadhar Card copy"),
    form_16_or_it_returns: UploadFile = File(None, description="Form 16 or Income Tax Returns"),
    db: Session = Depends(get_db)
):
    """
    Updates specific documents for an existing employee. Only provided files will be updated.
    """
    db_documents = db.query(models.EmployeeDocuments).filter(
        models.EmployeeDocuments.employee_id == employee_id
    ).first()
    if not db_documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for employee ID {employee_id} not found. Use POST to upload first."
        )
    
    db_documents.updated_at = datetime.now()

    files_to_process = {
        "resume": resume,
        "educational_certificates": educational_certificates,
        "offer_letters": offer_letters,
        "pan_card": pan_card,
        "aadhar_card": aadhar_card,
        "form_16_or_it_returns": form_16_or_it_returns,
    }

    for doc_field, uploaded_file in files_to_process.items():
        if uploaded_file and uploaded_file.filename: # Only process if a new file is provided for this field
            try:
                file_path = save_uploaded_file(uploaded_file, employee_id)
                setattr(db_documents, doc_field, file_path)
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing {doc_field}: {str(e)}"
                )

    try:
        db.add(db_documents)
        db.commit()
        db.refresh(db_documents)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document record: {str(e)}"
        )
    return db_documents

# ---------------------
# 🗑️ Endpoint: Delete All Documents for an Employee
# ---------------------
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_documents(employee_id: int, db: Session = Depends(get_db)):
    """
    Deletes all document records and associated files for a specific employee.
    """
    db_documents = db.query(models.EmployeeDocuments).filter(
        models.EmployeeDocuments.employee_id == employee_id
    ).first()
    if not db_documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for employee ID {employee_id} not found."
        )

    try:
        # Delete the physical files from the server
        employee_doc_dir = os.path.join(UPLOAD_DIR, str(employee_id))
        if os.path.exists(employee_doc_dir):
            shutil.rmtree(employee_doc_dir) # Recursively delete the employee's document directory

        # Delete the database record
        db.delete(db_documents)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document record or files: {str(e)}"
        )
    return # No content returned for 204

# ---------------------
# ⬇️ Endpoint: Download a Specific Document
# (Optional, but highly recommended for a full CRUD for files)
# ---------------------
from fastapi.responses import FileResponse

@router.get("/{employee_id}/{document_type}", response_class=FileResponse)
def download_employee_document(employee_id: int, document_type: str, db: Session = Depends(get_db)):
    """
    Downloads a specific document for an employee.
    Document types: resume, educational_certificates, offer_letters, pan_card, aadhar_card, form_16_or_it_returns.
    """
    db_documents = db.query(models.EmployeeDocuments).filter(
        models.EmployeeDocuments.employee_id == employee_id
    ).first()
    if not db_documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for employee ID {employee_id} not found."
        )

    # Get the file path from the database record
    file_path = getattr(db_documents, document_type, None)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type '{document_type}' not found for employee ID {employee_id}."
        )

    # Ensure the file actually exists on the server
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found on server at path: {file_path}. It might have been moved or deleted externally."
        )

    # Determine media type dynamically or use a sensible default
    media_type = "application/octet-stream" # Default for unknown binary files
    if file_path.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif file_path.endswith(".png"):
        media_type = "image/png"
    elif file_path.endswith(".doc") or file_path.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    # Add more as needed

    return FileResponse(path=file_path, media_type=media_type, filename=os.path.basename(file_path))
