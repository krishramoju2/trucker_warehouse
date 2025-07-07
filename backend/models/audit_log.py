from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from backend.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    action = Column(String(50))  # e.g., 'CREATE', 'UPDATE', 'DELETE'
    table_name = Column(String(100))
    record_id = Column(Integer)
    description = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
 
