from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import NotificationService
from ..services import UserService
from pydantic import BaseModel
from ..config import settings

router = APIRouter(prefix="/notifications", tags=["Notifications"])

notification_service = NotificationService(settings.TELEGRAM_BOT_TOKEN)
user_service = UserService()


class NotificationRequest(BaseModel):
    message: str


@router.post("/send/{user_id}")
def send_notification(
        user_id: int,
        request: NotificationRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(notification_service.send_message, user.telegram_id, request.message)
    return {"status": "Notification sent", "message": request.message}
