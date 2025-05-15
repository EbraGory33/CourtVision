from fastapi import FastAPI
#from app.routes import auth, odds, parlays, chat, stats, teams, players,  ws
from app.routes import players, teams

app = FastAPI(title="CourtVision API")
"""
app.include_router(auth.router)
app.include_router(odds.router)
app.include_router(parlays.router)
app.include_router(chat.router)
app.include_router(stats.router)
"""
# Include API routes
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
'''
app.include_router(ws.router, prefix="/ws", tags=["WebSockets"])
'''
@app.get("/")
def home():
    return {"message": "Welcome to CourtVision API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



