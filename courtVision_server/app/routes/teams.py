from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from app.models.models import *
from app.schemas.team import TeamBase
from sqlalchemy.future import select

from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/", response_model=list[TeamBase])
def get_players(db: Session = Depends(get_db)):
    result = db.execute(select(Team))    
    players = result.scalars().all()
    return players

@router.get("/{team_id}", response_model=TeamBase)
def get_player(team_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Team).filter_by(id=team_id))
    player = result.scalars().first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

