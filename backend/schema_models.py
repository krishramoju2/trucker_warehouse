from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class EmployeeInfo(Base):
    __tablename__ = "employee_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    address = Column(Text, nullable=False)
    contact_number = Column(String(15), nullable=False, unique=True)
    pan_number = Column(String(10), nullable=False, unique=True)
    aadhar_number = Column(String(12), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    documents = relationship(
        "EmployeeDocuments",
        backref="employee",
        cascade="all, delete",
        passive_deletes=True
    )


class EmployeeDocuments(Base):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_info.id", ondelete="CASCADE"), nullable=False)
    resume = Column(Text, nullable=False)
    educational_certificates = Column(Text, nullable=False)
    offer_letters = Column(Text, nullable=False)
    pan_card = Column(Text, nullable=False)
    aadhar_card = Column(Text, nullable=False)
    form_16_or_it_returns = Column(Text, nullable=False)

