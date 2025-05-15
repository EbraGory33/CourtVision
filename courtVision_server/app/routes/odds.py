import requests
from fastapi import APIRouter

router = APIRouter(prefix="/odds", tags=["Odds"])

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/"

@router.get("/live")
def get_live_odds():
    response = requests.get(f"{ODDS_API_URL}basketball_nba/odds/?apiKey=YOUR_API_KEY")
    return response.json()
