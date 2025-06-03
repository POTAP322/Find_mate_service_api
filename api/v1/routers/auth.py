from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreateRequest
from ..services import UserService, NotificationService
from ..security import validate_telegram_data
from ..models import User
from ..config import settings

router = APIRouter(tags=["Auth"])

user_service = UserService()
notification_service = NotificationService(settings.TELEGRAM_BOT_TOKEN)


def notify_user_about_auth(user_id: int, db: Session):
    user = user_service.get_user(db, user_id)
    if not user:
        return

    message = "✅ Вы успешно авторизировались в сервисе FindMate"
    notification_service.send_message(user.telegram_id, message)


@router.post("/auth/telegram")
def telegram_auth(
    user_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    telegram_id = user_data.get("id")
    username = user_data.get("username")
    auth_hash = user_data.get("hash")

    if not telegram_id or not username or not auth_hash:
        raise HTTPException(status_code=400, detail="Missing required fields")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    is_valid = validate_telegram_data(user_data, bot_token)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid Telegram data")

    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()

    if not user:
        new_user = UserCreateRequest(
            telegram_id=str(telegram_id),
            username=username,
            description=""
        )
        user = user_service.create_user(db, new_user)
        # Только что созданный пользователь — отправляем приветственное сообщение
        background_tasks.add_task(notify_user_about_auth, user.id, db)
    else:
        # Уже существующий пользователь — просто уведомляем о входе
        background_tasks.add_task(notify_user_about_auth, user.id, db)

    return {"user": user}