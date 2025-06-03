from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreateRequest, UserResponse, UserUpdateUsernameRequest, UserUpdateDescriptionRequest, \
    UserUpdateAccountStatusRequest, UserUpdateCurrentPartnerRequestsRequest
from ..services import UserService, NotificationService
from ..config import settings

router = APIRouter(prefix="/users", tags=["Users"])

user_service = UserService()
notification_service = NotificationService(settings.TELEGRAM_BOT_TOKEN)


def notify_user_about_account_status_change(user_id: int, new_status: str, db: Session):
    user = user_service.get_user(db, user_id)
    if not user:
        return

    message = f"✅ Ваш статус аккаунта изменён: теперь ваш статус — {new_status.capitalize()}"
    notification_service.send_message(user.telegram_id, message)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.delete("/by_telegram_id/{telegram_id}")
def delete_user_by_telegram_id(telegram_id: str, db: Session = Depends(get_db)):
    user_service.delete_user_by_telegram_id(db, telegram_id)
    return {"message": "User deleted successfully"}


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}/username", response_model=UserResponse)
def update_username(user_id: int, username_data: UserUpdateUsernameRequest, db: Session = Depends(get_db)):
    return user_service.update_username(db, user_id, username_data)


@router.patch("/{user_id}/description", response_model=UserResponse)
def update_description(user_id: int, description_data: UserUpdateDescriptionRequest, db: Session = Depends(get_db)):
    return user_service.update_description(db, user_id, description_data)


@router.patch("/{user_id}/account_status", response_model=UserResponse)
def update_account_status(
    user_id: int,
    account_status_data: UserUpdateAccountStatusRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    result = user_service.update_account_status(db, user_id, account_status_data)

    # Отправляем уведомление в фоне
    background_tasks.add_task(
        notify_user_about_account_status_change,
        user_id,
        account_status_data.account_status,
        db
    )

    return result


@router.patch("/{user_id}/current_partner_requests", response_model=UserResponse)
def update_current_partner_requests(
    user_id: int,
    current_partner_requests_data: UserUpdateCurrentPartnerRequestsRequest,
    db: Session = Depends(get_db)
):
    return user_service.update_current_partner_requests(db, user_id, current_partner_requests_data)