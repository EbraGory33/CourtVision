from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# 🔹 Team Schema
class TeamBase(BaseModel):
    name: str
    abbreviation: str
    city: str
    conference: str
    division: str
    founded: int
    championships: int
    logo: Optional[str] = None

class TeamCreate(TeamBase):  # Schema for creating a team
    pass

class TeamResponse(TeamBase):  # Schema for returning team data
    id: int

    class Config:
        orm_mode = True  # Enables ORM compatibility

# 🔹 Game Schema
class GameBase(BaseModel):
    season_id: int
    date: date
    home_team_id: int
    away_team_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    location: str

class GameCreate(GameBase):  # Schema for creating a game
    pass

class GameResponse(GameBase):  # Schema for returning game data
    id: int

    class Config:
        orm_mode = True

# 🔹 PlayerStats Schema
class PlayerStatsBase(BaseModel):
    player_id: int
    game_id: int
    minutes_played: float
    points: int
    assists: int
    rebounds: int
    offensive_rebounds: int
    defensive_rebounds: int
    steals: int
    blocks: int
    turnovers: int
    personal_fouls: int
    field_goals_made: int
    field_goals_attempted: int
    three_pointers_made: int
    three_pointers_attempted: int
    free_throws_made: int
    free_throws_attempted: int
    plus_minus: int

class PlayerStatsCreate(PlayerStatsBase):  # Schema for creating player stats
    pass

class PlayerStatsResponse(PlayerStatsBase):  # Schema for returning player stats
    id: int

    class Config:
        orm_mode = True
