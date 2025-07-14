import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import OperationalError

# ---------------------------
# 🔧 Database Configuration
# ---------------------------

# Default PostgreSQL connection string
DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5432/warehouse_db"

# Get URL from environment or fallback to default
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Optional: Log DB URL (hide password in production!)
print(f"📡 Connecting to database: {DATABASE_URL}")

# ---------------------------
# 🚀 SQLAlchemy Initialization
# ---------------------------

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except OperationalError as e:
    raise RuntimeError(f"❌ Failed to connect to database: {e}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# ---------------------------
# 🧱 Dependency - DB Session
# ---------------------------

def get_db() -> Session:
    """
    Dependency that provides a database session for FastAPI routes.
    Used via Depends(get_db) in your routes to auto-handle session closing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
