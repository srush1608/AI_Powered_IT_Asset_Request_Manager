
from sqlalchemy import Column, Integer, String, Boolean
# from models import Base
from backend.database import Base


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    department = Column(String)
    designation = Column(String)
    gender = Column(String)
    employee_status = Column(Boolean, default=True)
    password = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)    

    def __repr__(self):
        return f"<Employee(name={self.first_name} {self.last_name}, email={self.email})>"
