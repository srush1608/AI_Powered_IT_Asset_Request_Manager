# create_tables.py

from backend.database import Base, engine  
from backend.models import Employee  

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
