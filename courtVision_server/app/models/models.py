from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from ..db.database import Base

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(9), unique=True, nullable=False)

    games = relationship("Game", back_populates="season")
    players = relationship("PlayerBySeasons", back_populates="season")
    teams = relationship("TeamBySeasons", back_populates="season")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    abbreviation = Column(String(5), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    conference = Column(String(50), nullable=False)
    division = Column(String(50), nullable=False)
    founded = Column(Integer, nullable=False)
    logo = Column(String, nullable=True)  # Store image paths instead of ImageField
    
    team_by_seasons = relationship("TeamBySeasons", back_populates="team")
    #history = relationship("TeamHistory", back_populates="team")
'''
class TeamHistory(Base):
    __tablename__ = "team_history"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)  # Link to the main team
    season_year = Column(Integer, nullable=False)  # The season or year for the record
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)  # Could be the old name if changed
    conference = Column(String(50), nullable=False)
    division = Column(String(50), nullable=False)
    founded = Column(Integer, nullable=False)  # Founding year of that particular location/team
    logo = Column(String, nullable=True)  # Store image paths for logos per year/season

    team = relationship("Team", back_populates="history")
'''


class TeamBySeasons(Base):
    __tablename__ = "team_by_seasons"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    division_ranking = Column(Integer, nullable=True)
    conference_ranking = Column(Integer, nullable=True)
    league_ranking = Column(Integer, nullable=True)
    
    team = relationship("Team", back_populates="team_by_seasons")
    season = relationship("Season", back_populates="teams")
    stats = relationship("TeamGameLog", back_populates="team")
    home_games = relationship("Game", foreign_keys="[Game.home_team_id]", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="[Game.away_team_id]", back_populates="away_team")

    
class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    height = Column(String(10), nullable=True)  
    weight = Column(Integer, nullable=True)  
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(50), nullable=True)
    college = Column(String(100), nullable=True)
    jersey_number = Column(Integer, nullable=True)
    experience = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=True)
    image = Column(String, nullable=True)  

    player_by_seasons = relationship("PlayerBySeasons", back_populates="player")

class PlayerBySeasons(Base):
    __tablename__ = "player_by_seasons"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)  # Player may change teams during season

    games_played = Column(Integer, default=0)
    games_started = Column(Integer, default=0)
    
    minutes_played_per_game = Column(Float, default=0.0)

    # Per-game stats
    points_per_game = Column(Float, default=0.0)
    assists_per_game = Column(Float, default=0.0)
    offensive_rebounds_per_game = Column(Float, default=0.0)
    defensive_rebounds_per_game = Column(Float, default=0.0)
    rebounds_per_game = Column(Float, default=0.0)
    steals_per_game = Column(Float, default=0.0)
    blocks_per_game = Column(Float, default=0.0)
    turn_over_per_game = Column(Float, default=0.0)
    personal_fouls_per_game = Column(Float, default=0.0)
    
    # Total stats
    total_points = Column(Integer, default=0)
    total_assists = Column(Integer, default=0)
    total_offensive_rebounds = Column(Integer, default=0)
    total_defensive_rebounds = Column(Integer, default=0)
    total_rebounds = Column(Integer, default=0)
    total_steals = Column(Integer, default=0)
    total_blocks = Column(Integer, default=0)
    total_turnovers = Column(Integer, default=0)
    total_personal_fouls = Column(Integer, default=0)

    # Shooting - per game
    field_goal_made_per_game = Column(Float, default=0.0)
    field_goal_attempted_per_game = Column(Float, default=0.0)
    field_goal_percentage_per_game = Column(Float, default=0.0)

    three_point_made_per_game = Column(Float, default=0.0)
    three_point_attempted_per_game = Column(Float, default=0.0)
    three_point_percentage_per_game = Column(Float, default=0.0)

    free_throw_made_per_game = Column(Float, default=0.0)
    free_throw_attempted_per_game = Column(Float, default=0.0)
    free_throw_percentage_per_game = Column(Float, default=0.0)

    # Shooting - totals
    total_field_goal = Column(Integer, default=0)
    total_field_goal_attempted = Column(Integer, default=0)
    field_goal_percentage = Column(Float, default=0.0)

    total_three_point_made = Column(Float, default=0.0)
    total_three_point_attempted = Column(Float, default=0.0)
    three_point_percentage = Column(Float, default=0.0)
    
    total_free_throw_made = Column(Float, default=0.0)
    total_free_throw_attempted = Column(Float, default=0.0)
    free_throw_percentage = Column(Float, default=0.0)

    player = relationship("Player", back_populates="player_by_seasons")
    season = relationship("Season", back_populates="players")
    stats = relationship("PlayerGameLog", back_populates="player")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    date = Column(Date, nullable=False)
    home_team_id = Column(Integer, ForeignKey("team_by_seasons.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("team_by_seasons.id"), nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    location = Column(String(255), nullable=False)

    # New fields
    pace = Column(Float, nullable=True)  # Estimated pace of play
    possessions = Column(Integer, nullable=True)  # Number of possessions per team
    home_rest_days = Column(Integer, nullable=True)  # Days since last game
    away_rest_days = Column(Integer, nullable=True)
    referee = Column(String(100), nullable=True)  # Main referee
    is_back_to_back = Column(Boolean, default=False)  # Is either team on a back-to-back?

    season = relationship("Season", back_populates="games")
    home_team = relationship("TeamBySeasons", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("TeamBySeasons", foreign_keys=[away_team_id], back_populates="away_games")
    player_stats = relationship("PlayerGameLog", back_populates="game")
    team_stats = relationship("TeamGameLog", back_populates="game")

class PlayerGameLog(Base):
    __tablename__ = "player_game_log"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    player_season_id = Column(Integer, ForeignKey("player_by_seasons.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    minutes_played = Column(Float, nullable=False)
    points = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    offensive_rebounds = Column(Integer, default=0)
    defensive_rebounds = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    three_pointers_made = Column(Integer, default=0)
    three_pointers_attempted = Column(Integer, default=0)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)

    # Advanced stats
    efficiency = Column(Float, nullable=True)  # PER, Win Shares, etc.
    usage_rate = Column(Float, nullable=True)  # % of team possessions used
    true_shooting_percentage = Column(Float, nullable=True)  # Adjusted for FTs and 3PTs
    plus_minus = Column(Integer, default=0)  # Impact on team performance
    on_off_rating = Column(Float, nullable=True)  # Net rating when on/off the court

    # Clutch performance1   
    clutch_points = Column(Integer, nullable=True)  # Points in close games
    clutch_field_goal_percentage = Column(Float, nullable=True)

    player = relationship("PlayerBySeasons", back_populates="stats")
    game = relationship("Game", back_populates="player_stats")

class TeamGameLog(Base):
    __tablename__ = "team_game_log"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    team_season_id = Column(Integer, ForeignKey("team_by_seasons.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    points = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    three_pointers_made = Column(Integer, default=0)
    three_pointers_attempted = Column(Integer, default=0)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)

    # Advanced metrics
    offensive_rating = Column(Float, nullable=True)  # Points per 100 possessions
    defensive_rating = Column(Float, nullable=True)  # Opponent points per 100 possessions
    net_rating = Column(Float, nullable=True)  # OffRtg - DefRtg
    assist_to_turnover_ratio = Column(Float, nullable=True)

    # Clutch performance
    clutch_points = Column(Integer, nullable=True)  # Points in close games
    clutch_field_goal_percentage = Column(Float, nullable=True)

    team = relationship("TeamBySeasons", back_populates="stats")
    game = relationship("Game", back_populates="team_stats")
"""
class InjuryReport(Base):
    __tablename__ = "injury_reports"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True)
    status = Column(String(50))  # e.g. "Out", "Questionable", "Probable"
    reason = Column(String(255), nullable=True)
    reported_date = Column(Date, nullable=False)

class StartingLineup(Base):
    __tablename__ = "starting_lineups"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    position = Column(String(10))  # PG, SG, etc.
"""