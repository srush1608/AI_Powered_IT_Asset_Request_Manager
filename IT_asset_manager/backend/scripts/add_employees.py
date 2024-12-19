import sys
import os
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import Employee
import bcrypt

# Add the backend directory to sys.path so you can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

def create_employee_data():
    # Create a new session
    session = SessionLocal()

    try:
        # Hash the password before storing it
        password_hash = bcrypt.hashpw("Pass@123".encode('utf-8'), bcrypt.gensalt())

        # Create employee instances
        employee1 = Employee(
            employee_id="E1234",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123-456-7890",
            department="IT",
            designation="Manager",
            gender="Male",
            employee_status=True,
            password=password_hash.decode('utf-8')  # Store the hashed password
        )

        # Add employee to the session
        session.add(employee1)

        # Commit the transaction to save the data in the database
        session.commit()

        print("Employee added successfully!")

    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()

    finally:
        session.close()

# Call the function to add employee data
create_employee_data()
