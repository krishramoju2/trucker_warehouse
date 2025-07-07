from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import employee, documents, auth, files
from backend.routers import admin  # import admin router here

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Warehouse API running"}

# Include all routers
app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(documents.router)
app.include_router(files.router)
app.include_router(admin.router)  # included safely
