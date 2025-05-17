from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserGameCreateRequest, UserGameResponse
from ..services import UserGameService

router = APIRouter(prefix="/usergames", tags=["UserGames"])
user_game_service = UserGameService()

@router.post("/", response_model=UserGameResponse)
def create_user_game(user_game: UserGameCreateRequest, db: Session = Depends(get_db)):
    try:
        return user_game_service.create_user_game(db, user_game)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_game_id}")
def delete_user_game(user_game_id: int, db: Session = Depends(get_db)):
    user_game_service.delete_user_game(db, user_game_id)
    return {"message": "UserGame deleted successfully"}