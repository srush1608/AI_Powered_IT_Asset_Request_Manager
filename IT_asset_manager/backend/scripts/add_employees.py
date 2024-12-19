import sys
import os
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import Employee
import bcrypt
import sys



# Add the backend directory to sys.path so you can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
# print("0------------------------------")
# print(sys.path)


def create_employee_data():
    # Create a new session
    session = SessionLocal()
    
    try:
        # Hash passwords (using different passwords for demonstration)
        password1 = bcrypt.hashpw("Pass@123".encode('utf-8'), bcrypt.gensalt())
        password2 = bcrypt.hashpw("Pass@456".encode('utf-8'), bcrypt.gensalt())
        password3 = bcrypt.hashpw("Pass@789".encode('utf-8'), bcrypt.gensalt())
        password4 = bcrypt.hashpw("Pass@321".encode('utf-8'), bcrypt.gensalt())
        password5 = bcrypt.hashpw("Pass@654".encode('utf-8'), bcrypt.gensalt())

        # Create employee instances
        employees = [
            Employee(
                employee_id="E1001",
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="123-456-7890",
                department="IT",
                designation="Senior Developer",
                gender="Male",
                employee_status=True,
                password=password1.decode('utf-8')
            ),
            Employee(
                employee_id="E1002",
                first_name="Sarah",
                last_name="Johnson",
                email="sarah.johnson@example.com",
                phone="987-654-3210",
                department="HR",
                designation="HR Manager",
                gender="Female",
                employee_status=True,
                password=password2.decode('utf-8')
            ),
            Employee(
                employee_id="E1003",
                first_name="Michael",
                last_name="Smith",
                email="michael.smith@example.com",
                phone="456-789-0123",
                department="IT Support",
                designation="Support Specialist",
                gender="Male",
                employee_status=True,
                password=password3.decode('utf-8')
            ),
            Employee(
                employee_id="E1004",
                first_name="Emily",
                last_name="Brown",
                email="emily.brown@example.com",
                phone="789-012-3456",
                department="IT",
                designation="Project Manager",
                gender="Female",
                employee_status=True,
                password=password4.decode('utf-8')
            ),
            Employee(
                employee_id="E1005",
                first_name="David",
                last_name="Wilson",
                email="david.wilson@example.com",
                phone="321-654-0987",
                department="IT Support",
                designation="Technical Support",
                gender="Male",
                employee_status=True,
                password=password5.decode('utf-8')
            )
        ]

        # Add all employees to the session
        for employee in employees:
            session.add(employee)
            print("________________________________________")
            print(employee)

        # Commit the transaction to save the data in the database
        session.commit()
        
        print("Employees added successfully!")
        
        # Print the added employees' details for verification
        print("\nAdded Employees:")
        for employee in employees:
            print(f"ID: {employee.employee_id}, Name: {employee.first_name} {employee.last_name}, "
                  f"Department: {employee.department}, Email: {employee.email}")

    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()
    
    finally:
        session.close()

# Call the function to add employee data
if __name__ == "__main__":
    create_employee_data()