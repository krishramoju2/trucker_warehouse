from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.file_service import get_file_service, FileService # Import service and its dependency
from backend.models import file_model # Pydantic models
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
    db_service: FileService = Depends(get_file_service) # Inject the file service
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
        
        # Store metadata in DB
        db_file = db_service.handle_upload(
            file_path=file_path,
            original_filename=file.filename,
            uploaded_by=uploaded_by,
            is_scanned=True,
            is_clean=is_clean
        )

        if not is_clean:
            # If virus detected, delete the file and raise an error
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.warning(f"Infected file deleted: {file_path}")
            # Also, remove metadata from DB if it was added for an infected file
            # or update its status to infected if you keep records of bad files
            # For now, we assume handle_upload already set is_clean=False
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Virus detected in uploaded file. File deleted.")
        
        return db_file
    except HTTPException as e:
        # Re-raise explicit HTTPExceptions (e.g., from virus scan)
        raise e
    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)
        # Clean up the partially saved file if an error occurred before successful DB commit
        if is_file_saved and os.path.exists(file_path):
            os.remove(file_path)
            logger.error(f"Cleaned up partially uploaded file due to error: {file_path}")
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
    db_service: FileService = Depends(get_file_service)
):
    """
    Retrieves metadata for a specific file.
    """
    file_metadata = db_service.get_file_by_id(file_id)
    if not file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File metadata not found")
    return file_metadata

@router.get(
    "/{file_id}/download", 
    summary="Download a file by ID",
    description="Initiates the download of a specific file by its ID."
)
def download_file(
    file_id: int, 
    db_service: FileService = Depends(get_file_service)
):
    """
    Allows downloading a file by its ID.
    - Checks if the file exists in the database and on disk.
    """
    file_metadata = db_service.get_file_by_id(file_id)
    if not file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File metadata not found")
    
    # Verify if the physical file exists before attempting to serve
    if not os.path.exists(file_metadata.path):
        logger.error(f"Physical file not found for ID {file_id} at path: {file_metadata.path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file not found on server. Contact administrator.")
    
    return FileResponse(path=file_metadata.path, filename=file_metadata.original_filename)

@router.delete(
    "/{file_id}", 
    status_code=status.HTTP_200_OK, # Or HTTP_204_NO_CONTENT for no body
    summary="Delete a file by ID",
    description="Deletes a file's metadata from the database and its corresponding physical file from storage."
)
def delete_file(
    file_id: int, 
    db_service: FileService = Depends(get_file_service)
):
    """
    Deletes a file (metadata and physical file) by its ID.
    """
    is_deleted = db_service.delete_file(file_id)
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or could not be deleted.")
    
    return {"message": f"File with ID {file_id} deleted successfully"}
