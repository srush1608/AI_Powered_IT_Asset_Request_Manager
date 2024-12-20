from . import models
from sqlalchemy.orm import Session
from .models import Employee, AssetRequest, RequestStatus
from backend.scripts.add_employees import Employee

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()


def create_asset_request(db: Session, employee_id: int, asset_name: str, configuration: str, reason: str):
    # Check if employee exists before proceeding
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise Exception(f"Employee with id {employee_id} not found")

    request = AssetRequest(
        employee_id=employee_id,
        asset_name=asset_name,
        configuration=configuration,
        reason=reason,
        status=RequestStatus.pending
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request



def update_asset_request_status(db: Session, request_id: int, status: RequestStatus):
    request = db.query(AssetRequest).filter(AssetRequest.id == request_id).first()
    if request:
        request.status = status
        db.commit()
        db.refresh(request)
    return request
