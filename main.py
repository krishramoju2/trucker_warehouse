from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import employee, documents

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Warehouse API running"}

app.include_router(employee.router)
app.include_router(documents.router)
