from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import requests

from ..database import get_db
from ..models import User
from ..services import UserService, NotificationService
from ..config import settings
from ..schemas import UpgradeRequest

router = APIRouter(prefix="/payments", tags=["Payments"])

user_service = UserService()
notification_service = NotificationService(settings.TELEGRAM_BOT_TOKEN)
bot_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


# --- Эндпоинт для создания инвойса ---
@router.get("/invoice/{duration}")
def generate_invoice(duration: str, chat_id: int):
    prices = {
        "day": [{"label": "1 день Premium", "amount": 1}], #20
        "week": [{"label": "1 неделя Premium", "amount": 65}],
        "forever": [{"label": "Premium навсегда", "amount": 200}]
    }

    if duration not in prices:
        raise HTTPException(status_code=400, detail="Invalid duration")

    payload = {
        "chat_id": chat_id,
        "title": f"Premium подписка ({duration})",
        "description": "Подписка на повышение статуса аккаунта",
        "payload": f"upgrade_{duration}",
        "provider_token": "stars",  # Telegram Stars
        "currency": "XTR",  # валюта — Telegram Stars
        "prices": prices[duration],
        "need_email": False,
        "need_name": False,
        "need_shipping_address": False
    }

    response = requests.post(f"{bot_url}/sendInvoice", json=payload)
    return response.json()


@router.post("/payment-success")
def handle_payment_success(data: dict, db: Session = Depends(get_db)):
    payload = data.get("message", {}).get("successful_payment", {}).get("invoice_payload")
    if not payload or not payload.startswith("upgrade_"):
        raise HTTPException(status_code=400, detail="Invalid payment payload")

    user_telegram_id = str(data["message"]["from"]["id"])
    duration = payload.replace("upgrade_", "")

    # Найди пользователя по telegram_id
    user = db.query(User).filter(User.telegram_id == user_telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обнови статус аккаунта
    if duration == "day":
        user.account_status = "premium"
        user.premium_expires_at = datetime.now() + timedelta(days=1)
    elif duration == "week":
        user.account_status = "premium"
        user.premium_expires_at = datetime.now() + timedelta(days=7)
    elif duration == "forever":
        user.account_status = "premium"
        user.premium_expires_at = None  # бессрочно

    db.commit()
    db.refresh(user)

    # Отправь уведомление
    notification_service.send_message(
        user.telegram_id,
        f"✅ Ваш статус изменён на 'Premium' на {duration}"
    )

    return {"status": "success"}

# --- Эндпоинт для обработки завершённого платежа ---
@router.post("/upgrade")
def upgrade_account(
    data: UpgradeRequest,
    db: Session = Depends(get_db)
):
    user = user_service.get_user(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.duration == "day":
        user.account_status = "premium"
        user.premium_expires_at = datetime.now() + timedelta(days=1)

    elif data.duration == "week":
        user.account_status = "premium"
        user.premium_expires_at = datetime.now() + timedelta(days=7)

    elif data.duration == "forever":
        user.account_status = "premium"
        user.premium_expires_at = None  # бессрочно
    else:
        raise HTTPException(status_code=400, detail="Invalid duration")

    db.commit()
    db.refresh(user)

    # Уведомляем пользователя
    message = f"✅ Ваш статус изменён на 'Premium' на {data.duration}"
    notification_service.send_message(user.telegram_id, message)

    return {"status": "success", "user": user}