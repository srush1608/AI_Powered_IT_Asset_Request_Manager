from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  

class Employee(Base):
    __tablename__ = 'employees'
    
    # Defining unique constraint for the 'email' column
    __table_args__ = (
        UniqueConstraint('email', name='employees_email_key'),
    )
    
    employee_id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)  # You can also add `unique=True` here
    phone = Column(String)
    department = Column(String)
    designation = Column(String)
    gender = Column(String)
    employee_status = Column(Boolean, default=True)
    password = Column(String)

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, first_name={self.first_name}, last_name={self.last_name})>"
