from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import auth, employee, documents, files, admin, stats, search
from backend.utils.semantic_index import build_index

build_index()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warehouse API",
    version="1.0.0",
    description="API for managing warehouse employee records, documents, search, and stats."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Warehouse API running"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(files.router, prefix="/files", tags=["File Upload"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(search.router, prefix="/search", tags=["Semantic Search"])

