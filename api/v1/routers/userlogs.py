from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserLogCreateRequest, UserLogResponse
from ..services import UserLogService

router = APIRouter(prefix="/userlogs", tags=["UserLogs"])
user_log_service = UserLogService()

@router.post("/", response_model=UserLogResponse)
def create_user_log(log: UserLogCreateRequest, db: Session = Depends(get_db)):
    return user_log_service.create_user_log(db, log)
