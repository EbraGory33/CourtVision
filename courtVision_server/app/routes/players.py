from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from app.models.models import *
from app.schemas.player import PlayerBase
from sqlalchemy.future import select

from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/", response_model=list[PlayerBase])
def get_players(db: Session = Depends(get_db)):
    result = db.execute(select(Player))    
    players = result.scalars().all()
    return players

@router.get("/{player_id}", response_model=PlayerBase)
def get_player(player_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Player).filter_by(id=player_id))
    player = result.scalars().first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
    
