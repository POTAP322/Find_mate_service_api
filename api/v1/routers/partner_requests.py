from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PartnerRequestCreateRequest, PartnerRequestResponse
from ..services import PartnerRequestService, UserService
from ..services import NotificationService
from ..config import settings

router = APIRouter(prefix="/partner-requests", tags=["PartnerRequests"])

partner_request_service = PartnerRequestService()
user_service = UserService()
notification_service = NotificationService(settings.TELEGRAM_BOT_TOKEN)


def notify_user_about_new_request(user_id: int, db: Session):
    user = user_service.get_user(db, user_id)
    if not user:
        return

    message = "✅ Ваш запрос на поиск напарника успешно создан!"
    notification_service.send_message(user.telegram_id, message)


@router.post("/", response_model=PartnerRequestResponse)
def create_partner_request(
    request: PartnerRequestCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    new_request = partner_request_service.create_partner_request(db, request)

    # Отправляем уведомление в фоне
    background_tasks.add_task(notify_user_about_new_request, new_request.user_id, db)

    return new_request


@router.delete("/{request_id}")
def delete_partner_request(request_id: int, db: Session = Depends(get_db)):
    partner_request_service.delete_partner_request(db, request_id)
    return {"message": "PartnerRequest deleted successfully"}