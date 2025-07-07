from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import employee, documents, auth  # new
from backend.admin import main as admin_main  # optional, if you have admin-specific routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Warehouse API running"}

# Include all routers
app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(documents.router)
app.include_router(admin_main.router)  # optional
