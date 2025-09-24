import random
from typing import List, Optional
from models.game_models import ROWS, COLS

def create_board() -> List[List[int]]:
    """Creates an empty Connect 4 board."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def is_valid_location(board: List[List[int]], col: int) -> bool:
    """Checks if a piece can be dropped in the given column."""
    return board[0][col] == 0

def get_next_open_row(board: List[List[int]], col: int) -> Optional[int]:
    """Finds the lowest empty row in a column."""
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None

def drop_piece(board: List[List[int]], row: int, col: int, piece: int):
    """Places a player's piece on the board."""
    board[row][col] = piece

def check_win(board: List[List[int]], piece: int) -> bool:
    """Checks if the given piece has won the game."""
    # Check horizontal, vertical, and diagonal locations
    # (Code is the same as the original, omitted for brevity but should be pasted here)
    # Check horizontal locations
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonals
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False


def is_draw(board: List[List[int]]) -> bool:
    """Checks if the game is a draw (board is full)."""
    return all(board[0][c] != 0 for c in range(COLS))

def get_computer_move(board: List[List[int]]) -> int:
    """Simple AI: chooses a random valid column."""
    valid_cols = [c for c in range(COLS) if is_valid_location(board, c)]
    return random.choice(valid_cols) if valid_cols else -1