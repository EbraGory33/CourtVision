from pydantic import BaseModel
from typing import Optional
from datetime import date

# 🔹 Player Schema
class PlayerBase(BaseModel):
    name: str | None = None
    position: str | None = None
    height: str | None = None
    weight: int | None = None
    birth_date: date | None = None
    nationality: str | None = None
    college: str | None = None
    is_active: bool | None = None
    image: str | None = None

class PlayerCreate(PlayerBase): # Schema for creating a player
    pass

class PlayerOut(PlayerBase): # Schema for returning player data
    id: int

    class Config:
        orm_mode = True

# 🔹 PlayerBySeason Schema
class PlayerBySeasonsBase(BaseModel):
    season_id: int
    team_id: Optional[int] = None

    jersey_number: Optional[int] = None
    experience: Optional[int] = 0
    games_played: Optional[int] = 0
    points_per_game: Optional[float] = 0.0
    assists_per_game: Optional[float] = 0.0
    rebounds_per_game: Optional[float] = 0.0
    field_goal_percentage: Optional[float] = 0.0
    three_point_percentage: Optional[float] = 0.0
    free_throw_percentage: Optional[float] = 0.0
    minutes_played_per_game: Optional[float] = 0.0

class PlayerBySeasonsCreate(PlayerBySeasonsBase):
    pass  # Same fields as base when creating

class PlayerBySeasonsUpdate(BaseModel):
    team_id: Optional[int] = None
    jersey_number: Optional[int] = None
    experience: Optional[int] = None
    games_played: Optional[int] = None
    points_per_game: Optional[float] = None
    assists_per_game: Optional[float] = None
    rebounds_per_game: Optional[float] = None
    field_goal_percentage: Optional[float] = None
    three_point_percentage: Optional[float] = None
    free_throw_percentage: Optional[float] = None
    minutes_played_per_game: Optional[float] = None

class PlayerBySeasonsResponse(PlayerBySeasonsBase):
    id: int

    class Config:
        orm_mode = True  # Important to read from SQLAlchemy models












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
