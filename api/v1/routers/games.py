from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import GameCreateRequest, GameResponse
from ..services import GameService

router = APIRouter(prefix="/games", tags=["Games"])
game_service = GameService()

@router.post("/", response_model=GameResponse)
def create_game(game: GameCreateRequest, db: Session = Depends(get_db)):
    return game_service.create_game(db, game)

@router.get("/{game_id}", response_model=GameResponse)
def read_game(game_id: int, db: Session = Depends(get_db)):
    db_game = game_service.get_game(db, game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game
@router.delete("/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    game_service.delete_game(db, game_id)
    return {"message": "Game deleted successfully"}
