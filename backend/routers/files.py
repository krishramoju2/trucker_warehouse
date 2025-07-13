from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, File
from sqlalchemy.orm import Session
from backend.database import get_db
# Removed: from backend.services.file_service import get_file_service, FileService
from backend.models import file_model # Pydantic models
# Assuming your SQLAlchemy ORM model for File is accessible via file_model.File
# If your ORM model is in a different location (e.g., backend.database.models),
# you would adjust this import accordingly.
from backend.models.file_model import File as FileORM # Assuming ORM model is named File within file_model module

from backend.utils.virus_scan import scan_file
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import logging
from typing import Annotated # For Python 3.9+ for clearer dependency injection
# from backend.auth.auth_handler import get_current_user # Uncomment if you have auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])

# Ensure this directory exists. Better to configure it via environment variable.
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    response_model=file_model.FileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new file",
    description="Uploads a file, performs a virus scan, and stores its metadata. Requires authentication."
)
async def upload_file(
    file: Annotated[UploadFile, File(description="The file to upload")],
    # uploaded_by: Annotated[str, Depends(get_current_user)], # Uncomment and adjust for actual user object
    # For now, using a simple string if auth is not integrated yet:
    uploaded_by: str, # In a real app, this would come from current_user
    db: Session = Depends(get_db) # Inject the database session directly
):
    """
    Handles the file upload process.
    - Saves the file temporarily.
    - Performs a virus scan.
    - If clean, stores file metadata in the database.
    - If infected, deletes the temporary file and raises an HTTPException.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    # Generate a unique filename to prevent conflicts and for security
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    is_file_saved = False # Flag to track if the file was successfully saved to disk
    try:
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            # Use `await file.read()` for large files to avoid blocking
            # For simplicity, using shutil.copyfileobj which works well with UploadFile.file
            shutil.copyfileobj(file.file, buffer)
        is_file_saved = True
        logger.info(f"File saved to temporary path: {file_path}")

        # Perform virus scan
        is_clean = scan_file(file_path)

        # Create a new File ORM object and add it to the database session
        db_file_orm = FileORM(
            path=file_path,
            original_filename=file.filename,
            uploaded_by=uploaded_by,
            is_scanned=True,
            is_clean=is_clean
        )
        db.add(db_file_orm)
        db.commit() # Commit the new file's metadata to the database
        db.refresh(db_file_orm) # Refresh to get the generated ID and other default values

        if not is_clean:
            # If virus detected, delete the physical file and raise an error
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.warning(f"Infected file deleted: {file_path}")
            # The metadata for the infected file remains in the DB, marked as not clean.
            # If you wish to remove the metadata for infected files, uncomment the lines below:
            # db.delete(db_file_orm)
            # db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Virus detected in uploaded file. File deleted.")

        # Convert the ORM model instance to the Pydantic response model
        return file_model.FileOut.from_orm(db_file_orm)
    except HTTPException as e:
        # Re-raise explicit HTTPExceptions (e.g., from virus scan or bad request)
        db.rollback() # Rollback any pending database changes in case of an HTTPException
        raise e
    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)
        # Clean up the partially saved file if an error occurred before successful DB commit
        if is_file_saved and os.path.exists(file_path):
            os.remove(file_path)
            logger.error(f"Cleaned up partially uploaded file due to error: {file_path}")
        db.rollback() # Rollback the database transaction if any other error occurred
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {e}"
        )
    finally:
        # Ensure the uploaded file's file-like object is closed
        await file.close()


@router.get(
    "/{file_id}",
    response_model=file_model.FileOut,
    summary="Get file metadata by ID",
    description="Retrieves the metadata (filename, path, uploader, etc.) for a specific file by its ID."
)
def get_file_meta(
    file_id: int,
    db: Session = Depends(get_db) # Inject the database session directly
):
    """
    Retrieves metadata for a specific file from the database.
    """
    # Query the database for the file metadata by ID
    file_metadata = db.query(FileORM).filter(FileORM.id == file_id).first()
    if not file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File metadata not found")
    # Convert the ORM model instance to the Pydantic response model
    return file_model.FileOut.from_orm(file_metadata)


@router.get(
    "/{file_id}/download",
    summary="Download a file by ID",
    description="Initiates the download of a specific file by its ID."
)
def download_file(
    file_id: int,
    db: Session = Depends(get_db) # Inject the database session directly
):
    """
    Allows downloading a file by its ID.
    - Checks if the file exists in the database and on disk.
    """
    # Query the database for the file metadata by ID
    file_metadata = db.query(FileORM).filter(FileORM.id == file_id).first()
    if not file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File metadata not found")

    # Verify if the physical file exists on disk before attempting to serve it
    if not os.path.exists(file_metadata.path):
        logger.error(f"Physical file not found for ID {file_id} at path: {file_metadata.path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file not found on server. Contact administrator.")

    # Return the file as a FileResponse
    return FileResponse(path=file_metadata.path, filename=file_metadata.original_filename)

@router.delete(
    "/{file_id}",
    status_code=status.HTTP_200_OK, # Or HTTP_204_NO_CONTENT for no body
    summary="Delete a file by ID",
    description="Deletes a file's metadata from the database and its corresponding physical file from storage."
)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db) # Inject the database session directly
):
    """
    Deletes a file (metadata and physical file) by its ID.
    """
    # Find the file metadata in the database
    file_to_delete = db.query(FileORM).filter(FileORM.id == file_id).first()

    if not file_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    # Store the file path before deleting the database record
    file_path = file_to_delete.path

    try:
        # Delete the file metadata from the database
        db.delete(file_to_delete)
        db.commit() # Commit the database deletion

        # Delete the physical file from disk
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Physical file deleted: {file_path}")
        else:
            logger.warning(f"Physical file not found on disk for ID {file_id} at path: {file_path}. Metadata deleted.")

        return {"message": f"File with ID {file_id} deleted successfully"}
    except Exception as e:
        db.rollback() # Rollback the database transaction if an error occurs during deletion
        logger.error(f"Error deleting file with ID {file_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {e}"
        )

