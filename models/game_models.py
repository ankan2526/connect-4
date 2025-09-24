from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- Constants ---
ROWS = 6
COLS = 7
PLAYER_1 = 1
PLAYER_2 = 2
COMPUTER_PLAYER = 2

# --- Pydantic Models ---

class GameState(BaseModel):
    """Represents the complete state of a single game."""
    game_id: str
    board: List[List[int]]
    current_player: int
    opponent_type: Literal['human', 'computer']
    game_over: bool = False
    winner: Optional[Literal[1, 2, 'draw']] = None

class CreateGameRequest(BaseModel):
    """Request model to create a new game."""
    opponent_type: Literal['human', 'computer']

class MoveRequest(BaseModel):
    """Request model for a player to make a move."""
    player: int
    col: int = Field(..., ge=0, lt=COLS)