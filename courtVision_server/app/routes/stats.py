import requests
from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/player/{player_id}")
def get_player_stats(player_id: str):
    response = requests.get(f"{STATS_API_URL}players/{player_id}/profile.json?api_key=YOUR_API_KEY")
    return response.json()

@router.get("/{player_id}/last_{games}_games", response_model=PlayerStatsSchema)
async def get_player_last_n_games(player_id: int, games: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PlayerStats)
        .where(PlayerStats.player_id == player_id)
        .order_by(PlayerStats.game_date.desc())  # Assuming game_date exists
        .limit(games)
    )
    stats = result.scalars().all()

    if not stats:
        raise HTTPException(status_code=404, detail="Player stats not found")

    return stats

@router.post("/track/{player_id}", response_model=PlayerStatsSchema)
async def track_players(player_id: int, db: AsyncSession = Depends(get_db)):
    return None


@router.get("/{team_id}/last_{games}_games", response_model=TeamStatsSchema)
async def get_player_last_n_games(team_id: int, games: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamStats)
        .where(TeamStats.team_id == team_id)
        .order_by(TeamStats.game_date.desc())  # Assuming game_date exists
        .limit(games)
    )
    stats = result.scalars().all()

    if not stats:
        raise HTTPException(status_code=404, detail="Player stats not found")

    return stats

@router.post("/track/{team_id}", response_model=TeamStatsSchema)
async def track_players(team_id: int, db: AsyncSession = Depends(get_db)):
    return None
    