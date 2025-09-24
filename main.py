from fastapi import FastAPI
from routers import games

app = FastAPI(
    title="Connect 4 API",
    description="A backend for the classic Connect 4 game, now neatly structured!",
    version="1.1.0"
)

# Include the game router
app.include_router(games.router)

@app.get("/", tags=["Status"])
def read_root():
    """Welcome endpoint."""
    return {"message": "Welcome to the Connect 4 API! 🎮"}