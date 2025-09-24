import uuid
from fastapi import APIRouter, HTTPException
from models.game_models import GameState, CreateGameRequest, MoveRequest, PLAYER_1, PLAYER_2, COMPUTER_PLAYER
from services import game_logic
from db.in_memory_db import games

# Create a router to group game-related endpoints
router = APIRouter(
    prefix="/games",
    tags=["Game Management & Play"]
)

@router.post("", response_model=GameState, status_code=201)
def create_game(request: CreateGameRequest):
    """Creates a new Connect 4 game."""
    game_id = str(uuid.uuid4())
    game = GameState(
        game_id=game_id,
        board=game_logic.create_board(),
        current_player=PLAYER_1,
        opponent_type=request.opponent_type
    )
    games[game_id] = game
    return game

@router.get("/{game_id}", response_model=GameState)
def get_game_status(game_id: str):
    """Retrieves the current state of a game."""
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.post("/{game_id}/move", response_model=GameState)
def make_move(game_id: str, move: MoveRequest):
    """Makes a move in a game."""
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    if move.player != game.current_player:
        raise HTTPException(status_code=400, detail="Not your turn")
    if not game_logic.is_valid_location(game.board, move.col):
        raise HTTPException(status_code=400, detail="Column is full")

    # Apply human player's move
    row = game_logic.get_next_open_row(game.board, move.col)
    game_logic.drop_piece(game.board, row, move.col, move.player)

    if game_logic.check_win(game.board, move.player):
        game.winner = move.player
        game.game_over = True
        return game
    if game_logic.is_draw(game.board):
        game.winner = 'draw'
        game.game_over = True
        return game

    game.current_player = PLAYER_2 if move.player == PLAYER_1 else PLAYER_1

    # Handle Computer's Turn
    if game.opponent_type == 'computer' and game.current_player == COMPUTER_PLAYER:
        computer_col = game_logic.get_computer_move(game.board)
        if computer_col != -1:
            comp_row = game_logic.get_next_open_row(game.board, computer_col)
            game_logic.drop_piece(game.board, comp_row, computer_col, COMPUTER_PLAYER)

            if game_logic.check_win(game.board, COMPUTER_PLAYER):
                game.winner = COMPUTER_PLAYER
                game.game_over = True
                return game
            if game_logic.is_draw(game.board):
                game.winner = 'draw'
                game.game_over = True
                return game

        game.current_player = PLAYER_1

    return game