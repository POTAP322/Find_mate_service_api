from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Text, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    account_status = Column(Enum('premium', 'standard'), nullable=False, default='standard')
    description = Column(String(500), nullable=False)
    current_partner_requests = Column(Integer, nullable=False, default=0)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

class UserGame(Base):
    __tablename__ = "usergames"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))

class PartnerRequest(Base):
    __tablename__ = "partnerrequests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    required_players = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    lifetime = Column(Integer, nullable=False)
    platform = Column(Enum('PC', 'Console', 'Mobile'), nullable=False)

class UserLog(Base):
    __tablename__ = "userlogs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    log_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    log_type = Column(Enum('info', 'warning', 'error'), nullable=True, default='info')
