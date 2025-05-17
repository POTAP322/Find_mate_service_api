from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PartnerRequestCreateRequest, PartnerRequestResponse
from ..services import PartnerRequestService

router = APIRouter(prefix="/partner-requests", tags=["PartnerRequests"])
partner_request_service = PartnerRequestService()

@router.post("/", response_model=PartnerRequestResponse)
def create_partner_request(request: PartnerRequestCreateRequest, db: Session = Depends(get_db)):
    return partner_request_service.create_partner_request(db, request)

@router.delete("/{request_id}")
def delete_partner_request(request_id: int, db: Session = Depends(get_db)):
    partner_request_service.delete_partner_request(db, request_id)
    return {"message": "PartnerRequest deleted successfully"}