from backend.database import engine, Base
import backend.models  # Ensure all models are imported and registered

def create_tables():
    print("🔧 Creating tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_tables()
