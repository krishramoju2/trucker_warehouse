from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, TIMESTAMP
from backend.database import Base

class EmployeeInfo(Base):
    __tablename__ = "employee_info"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    date_of_birth = Column(Date)
    address = Column(Text)
    contact_number = Column(String(15))
    pan_number = Column(String(10))
    aadhar_number = Column(String(12))
    created_at = Column(TIMESTAMP)

class EmployeeDocuments(Base):
    __tablename__ = "employee_documents"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_info.id", ondelete="CASCADE"))
    resume = Column(Text)
    educational_certificates = Column(Text)
    offer_letters = Column(Text)
    pan_card = Column(Text)
    aadhar_card = Column(Text)
    form_16_or_it_returns = Column(Text)