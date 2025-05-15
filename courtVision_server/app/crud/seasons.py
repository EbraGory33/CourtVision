from sqlalchemy.orm import Session
from app.models import Season
from app.schemas.season import SeasonCreate

def create_season(db: Session, season: SeasonCreate):
    db_season = Season(year=season.year)
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

def get_season(db: Session, season_id: int):
    return db.query(Season).filter(Season.id == season_id).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Season).offset(skip).limit(limit).all()

def delete_season(db: Session, season_id: int):
    db_season = db.query(Season).filter(Season.id == season_id).first()
    if db_season:
        db.delete(db_season)
        db.commit()
    return db_season
