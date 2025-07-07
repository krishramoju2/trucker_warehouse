from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import admin

app = FastAPI(title="Admin Panel API")

# Enable CORS (for frontend calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the admin router
app.include_router(admin.router)
