from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import admin, employee, documents, auth, files

app = FastAPI(
    title="Warehouse Admin API",
    version="1.0.0",
    description="API backend for managing warehouse employee data, documents, and statistics."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/files", tags=["File Uploads"])
