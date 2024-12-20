from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class RequestStatus(enum.Enum):
    approved = "approved"
    pending = "pending"
    rejected = "rejected"
    unavailable = "unavailable"

class AssetRequest(Base):
    __tablename__ = "asset_requests"
    
    id = Column(Integer, primary_key=True, index=True)  # Add primary key here
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)  # ForeignKey updated
    asset_name = Column(String, nullable=False)
    configuration = Column(String)
    reason = Column(String)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    
    employee = relationship("Employee")  # Relationship with Employee model
    
class Employee(Base):
    __tablename__ = 'employees'
    
    # Defining unique constraint for the 'email' column
    __table_args__ = (
        UniqueConstraint('email', name='employees_email_key'),
    )
    
    employee_id = Column(Integer, primary_key=True)  # employee_id is now the primary key (Integer)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)  
    phone = Column(String)
    department = Column(String)
    designation = Column(String)
    gender = Column(String)
    employee_status = Column(Boolean, default=True)
    password = Column(String)

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, first_name={self.first_name}, last_name={self.last_name})>"
