from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AccountStatus(str, Enum):
    premium = "premium"
    standard = "standard"

class Platform(str, Enum):
    PC = "PC"
    Console = "Console"
    Mobile = "Mobile"

class LogType(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"

class UserCreateRequest(BaseModel):
    telegram_id: str
    username: str
    account_status: AccountStatus = AccountStatus.standard
    description: str

class UserResponse(BaseModel):
    id: int
    telegram_id: str
    username: str
    account_status: AccountStatus
    description: str
    current_partner_requests: int

class GameCreateRequest(BaseModel):
    name: str

class GameResponse(BaseModel):
    id: int
    name: str

class UserGameCreateRequest(BaseModel):
    user_id: int
    game_id: int

class UserGameResponse(BaseModel):
    id: int
    user_id: int
    game_id: int

class PartnerRequestCreateRequest(BaseModel):
    user_id: int
    game_id: int
    required_players: int
    description: Optional[str]
    lifetime: int
    platform: Platform

class PartnerRequestResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    required_players: int
    description: Optional[str]
    created_at: datetime
    lifetime: int
    platform: Platform

class UserLogCreateRequest(BaseModel):
    user_id: int
    log_text: str
    log_type: LogType = LogType.info

class UserLogResponse(BaseModel):
    id: int
    user_id: int
    log_text: str
    created_at: datetime
    log_type: LogType

class UserUpdateUsernameRequest(BaseModel):
    username: str

class UserUpdateDescriptionRequest(BaseModel):
    description: str

class UserUpdateAccountStatusRequest(BaseModel):
    account_status: AccountStatus

class UserUpdateCurrentPartnerRequestsRequest(BaseModel):
    current_partner_requests: int