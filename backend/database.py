import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import OperationalError

# ---------------------------
# 🔧 Database Configuration
# ---------------------------

# Default fallback URL
DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5432/warehouse_db"

# Use env var DATABASE_URL or fallback to local
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Optional: Print for debug (remove in production)
print(f"📡 Connecting to database: {DATABASE_URL}")

# ---------------------------
# 🚀 SQLAlchemy Initialization
# ---------------------------

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except OperationalError as e:
    raise RuntimeError(f"❌ Failed to connect to database: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# 🧱 Dependency - DB Session
# ---------------------------

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
