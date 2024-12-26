import sys
import os
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Asset



# Add the backend directory to sys.path so you can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

def create_asset_data():
    # Create a new session
    session = SessionLocal()

    try:
        # Asset data
        assets = [
            Asset(asset_name="Laptop Dell XPS 13", configuration="Intel i7, 16GB RAM, 512GB SSD", category="Laptop", request_status="available"),
            Asset(asset_name="Desktop HP Elite", configuration="Intel i5, 8GB RAM, 1TB HDD", category="Desktop", request_status="approved"),
            Asset(asset_name="Laptop MacBook Pro", configuration="Apple M1, 16GB RAM, 1TB SSD", category="Laptop", request_status="pending"),
            Asset(asset_name="Desktop Lenovo ThinkCentre", configuration="Intel i7, 32GB RAM, 512GB SSD", category="Desktop", request_status="rejected"),
            Asset(asset_name="Laptop ASUS ZenBook", configuration="Intel i5, 8GB RAM, 256GB SSD", category="Laptop", request_status="available"),
            Asset(asset_name="Desktop Dell OptiPlex", configuration="Intel i9, 64GB RAM, 2TB SSD", category="Desktop", request_status="available"),
            Asset(asset_name="Laptop HP Spectre x360", configuration="Intel i7, 16GB RAM, 512GB SSD", category="Laptop", request_status="approved"),
            Asset(asset_name="Desktop Acer Predator", configuration="AMD Ryzen 9, 64GB RAM, 1TB SSD", category="Desktop", request_status="pending"),
            Asset(asset_name="Laptop Razer Blade 15", configuration="Intel i7, 32GB RAM, 1TB SSD", category="Laptop", request_status="approved"),
            Asset(asset_name="Desktop Microsoft Surface Studio", configuration="Intel i9, 64GB RAM, 1TB SSD", category="Desktop", request_status="unavailable"),
            Asset(asset_name="Laptop Microsoft Surface Laptop", configuration="Intel i5, 8GB RAM, 512GB SSD", category="Laptop", request_status="approved"),
            Asset(asset_name="Desktop MSI Trident", configuration="Intel i7, 16GB RAM, 512GB SSD", category="Desktop", request_status="rejected"),
            Asset(asset_name="Laptop HP Envy 13", configuration="Intel i5, 8GB RAM, 256GB SSD", category="Laptop", request_status="pending"),
            Asset(asset_name="Desktop iMac", configuration="Apple M1, 16GB RAM, 1TB SSD", category="Desktop", request_status="available"),
            Asset(asset_name="Laptop Lenovo ThinkPad X1", configuration="Intel i7, 16GB RAM, 1TB SSD", category="Laptop", request_status="approved")
        ]

        # Add all assets to the session
        for asset in assets:
            session.add(asset)

        # Commit the transaction to save the data in the database
        session.commit()

        print("Assets added successfully!")

        # Print the added assets' details for verification
        print("\nAdded Assets:")
        for asset in assets:
            print(f"ID: {asset.asset_id}, Name: {asset.asset_name}, Configuration: {asset.configuration}, "
                  f"Category: {asset.category}, Request Status: {asset.request_status}")

    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()

    finally:
        session.close()

# Call the function to add asset data
if __name__ == "__main__":
    create_asset_data()
