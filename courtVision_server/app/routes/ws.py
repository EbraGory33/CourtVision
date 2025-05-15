from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from courtVision_server.app.db.database import get_db
from courtVision_server.app.models.models import *
from courtVision_server.app.schemas.schemas import PlayerStatsSchema
from sqlalchemy.future import select

router = APIRouter()

@router.ws("/ws/{player_id}", response_model=PlayerStatsSchema)
async def live_stream_players_stats(player_id: int, db: AsyncSession = Depends(get_db)):
    return None