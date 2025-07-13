from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import auth, employee, documents, files, admin, stats, search
import os

# Optional: Avoid crashing build on Vercel/production when DB not ready
try:
    print("🗃️ Creating database tables...")
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ Could not create tables: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Warehouse API",
    version="1.0.0",
    description="API for managing warehouse employee records, documents, search, and stats."
)

# Enable CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health-check endpoint
@app.get("/")
def root():
    return {"message": "✅ Warehouse API running"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(files.router, prefix="/files", tags=["File Upload"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(search.router, prefix="/search", tags=["Semantic Search"])
