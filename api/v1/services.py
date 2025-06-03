from datetime import datetime, timedelta
import requests
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from .models import User, Game, UserGame, PartnerRequest, UserLog
from .schemas import UserCreateRequest, GameCreateRequest, UserGameCreateRequest, PartnerRequestCreateRequest, \
    UserLogCreateRequest, UserUpdateUsernameRequest, UserUpdateDescriptionRequest, UserUpdateAccountStatusRequest, \
    UserUpdateCurrentPartnerRequestsRequest


class UserService:
    def create_user(self, db: Session, user_data: UserCreateRequest) -> User:
        new_user = User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def delete_user(self, db: Session, user_id: int) -> None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        db.delete(user)
        db.commit()
    def delete_user_by_telegram_id(self, db: Session, telegram_id: str) -> None:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            raise ValueError("User not found")
        db.delete(user)
        db.commit()

    def get_user(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()

    def update_username(self, db: Session, user_id: int, username_data: UserUpdateUsernameRequest) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.username = username_data.username
        db.commit()
        db.refresh(user)
        return user

    def update_description(self, db: Session, user_id: int, description_data: UserUpdateDescriptionRequest) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.description = description_data.description
        db.commit()
        db.refresh(user)
        return user

    def update_account_status(self, db: Session, user_id: int, account_status_data: UserUpdateAccountStatusRequest) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.account_status = account_status_data.account_status
        db.commit()
        db.refresh(user)
        return user

    def update_current_partner_requests(self, db: Session, user_id: int, current_partner_requests_data: UserUpdateCurrentPartnerRequestsRequest) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.current_partner_requests = current_partner_requests_data.current_partner_requests
        db.commit()
        db.refresh(user)
        return user

    def downgrade_expired_premium_users(self, db: Session):
        now = datetime.now()
        users_to_downgrade = db.query(User).filter(
            User.account_status == "premium",
            User.premium_expires_at.is_not(None),
            User.premium_expires_at < now
        ).all()

        for user in users_to_downgrade:
            user.account_status = "standard"
            user.premium_expires_at = None

        if users_to_downgrade:
            db.commit()

class GameService:
    def create_game(self, db: Session, game_data: GameCreateRequest) -> Game:
        new_game = Game(**game_data.dict())
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return new_game

    def delete_game(self, db: Session, game_id: int) -> None:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        db.delete(game)
        db.commit()

    def get_game(self, db: Session, game_id: int) -> Game:
        return db.query(Game).filter(Game.id == game_id).first()

class UserGameService:
    def create_user_game(self, db: Session, user_game_data: UserGameCreateRequest) -> UserGame:
        # Проверяем, существует ли уже такая связь
        existing_user_game = db.query(UserGame).filter(
            UserGame.user_id == user_game_data.user_id,
            UserGame.game_id == user_game_data.game_id
        ).first()

        if existing_user_game:
            raise ValueError("This game is already associated with the user")

        new_user_game = UserGame(**user_game_data.dict())
        db.add(new_user_game)
        db.commit()
        db.refresh(new_user_game)
        return new_user_game

    def delete_user_game(self, db: Session, user_game_id: int) -> None:
        user_game = db.query(UserGame).filter(UserGame.id == user_game_id).first()
        if not user_game:
            raise ValueError("UserGame not found")
        db.delete(user_game)
        db.commit()

class PartnerRequestService:
    def create_partner_request(self, db: Session, request_data: PartnerRequestCreateRequest) -> PartnerRequest:
        user = db.query(User).get(request_data.user_id)
        if not user:
            raise ValueError("User not found")

        current_requests_count = user.current_partner_requests  # <-- используем поле модели

        if user.account_status == "standard" and current_requests_count >= 2:
            raise ValueError("Standard account can have at most 2 partner requests")
        elif user.account_status == "premium" and current_requests_count >= 10:
            raise ValueError("Premium account can have at most 10 partner requests")

        new_request = PartnerRequest(**request_data.dict())
        db.add(new_request)

        # Увеличиваем счетчик
        user.current_partner_requests += 1
        db.commit()
        db.refresh(new_request)
        return new_request

    def delete_partner_request(self, db: Session, request_id: int) -> None:
        request = db.query(PartnerRequest).filter(PartnerRequest.id == request_id).first()
        if not request:
            raise ValueError("PartnerRequest not found")

        user = db.query(User).get(request.user_id)
        if user:
            user.current_partner_requests -= 1
            if user.current_partner_requests < 0:
                user.current_partner_requests = 0

        db.delete(request)
        db.commit()

    def delete_expired_requests(self, db: Session) -> None:
        # Получаем текущее время
        now = datetime.now()

        # Получаем все запросы, у которых время жизни истекло
        expired_requests = db.query(PartnerRequest).filter(
            func.date_add(
                PartnerRequest.created_at,
                text(f"INTERVAL lifetime MINUTE")
            ) < now
        ).all()

        # Удаляем устаревшие запросы
        for request in expired_requests:
            db.delete(request)
        db.commit()

class UserLogService:
    def create_user_log(self, db: Session, log_data: UserLogCreateRequest) -> UserLog:
        new_log = UserLog(**log_data.dict())
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log


class NotificationService:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, chat_id: str, text: str):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        return response.json()