from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from courtVision_server.app.db.database import get_db
from courtVision_server.app.models.models import Parlay, Bet
from courtVision_server.app.schemas.schemas import ParlayCreate

router = APIRouter(prefix="/parlay", tags=["Parlay"])

@router.post("/create")
def create_parlay(parlay: ParlayCreate, db: Session = Depends(get_db)):
    new_parlay = Parlay(user_id=parlay.user_id, bet_type=parlay.bet_type, odds=parlay.odds, stake=parlay.stake)
    db.add(new_parlay)
    db.commit()
    return {"message": "Parlay created successfully"}
