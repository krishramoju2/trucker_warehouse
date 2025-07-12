from backend.database import engine
from backend.models import Base
import backend.schema_models
# This will create all tables defined in your SQLAlchemy models
if __name__ == "__main__":
    print("Creating tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")
