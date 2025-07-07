from sqlalchemy.orm import Session
from backend.models.audit_log import AuditLog
from datetime import datetime

def log_action(
    db: Session,
    username: str,
    action: str,
    table_name: str,
    record_id: int,
    description: str = ""
):
    log_entry = AuditLog(
        username=username,
        action=action,
        table_name=table_name,
        record_id=record_id,
        description=description,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
