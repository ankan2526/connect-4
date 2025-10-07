# app.py

import streamlit as st
import requests
import time

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/games"
PIECE_EMOJI = {0: "⚪", 1: "🔴", 2: "🟡"}
PAGE_TITLE = "Connect 4"
PAGE_ICON = "🕹️"

# --- API Helper Functions (Unchanged) ---

def create_game(opponent_type: str):
    """Starts a new game via the API."""
    try:
        response = requests.post(API_URL, json={"opponent_type": opponent_type})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the game server: {e}")
        return None

def make_move(game_id: str, player: int, col: int):
    """Makes a move in the current game via the API."""
    try:
        response = requests.post(f"{API_URL}/{game_id}/move", json={"player": player, "col": col})
        if response.status_code == 400:
            # Display a temporary warning for invalid moves
            st.toast("That column is full!", icon="⚠️")
            return st.session_state.game_state # Return current state on bad move
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the game server: {e}")
        return None

# --- UI Rendering Functions (Improved) ---

def render_board(board: list):
    """Renders the game board with emojis and custom styling."""
    board_html = "<div class='connect4-board'>"
    for row in board:
        board_html += "<div class='connect4-row'>"
        for cell in row:
            board_html += f"<div class='connect4-cell'>{PIECE_EMOJI.get(cell, '')}</div>"
        board_html += "</div>"
    board_html += "</div>"
    st.markdown(board_html, unsafe_allow_html=True)

def render_status_header(game: dict):
    """Displays the current turn or the winner in a styled header."""
    if game['game_over']:
        if game['winner'] == 'draw':
            st.markdown("<div class='game-status status-draw'>🤝 It's a Draw! 🤝</div>", unsafe_allow_html=True)
        else:
            winner_emoji = PIECE_EMOJI.get(game['winner'], '')
            st.markdown(f"<div class='game-status status-win'>🎉 Player {game['winner']} ({winner_emoji}) Wins! 🎉</div>", unsafe_allow_html=True)
    else:
        player_emoji = PIECE_EMOJI.get(game['current_player'], '')
        st.markdown(f"<div class='game-status status-turn'>Turn: Player {game['current_player']} ({player_emoji})</div>", unsafe_allow_html=True)

def inject_custom_css():
    """Injects CSS for a more modern and interactive game UI."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

            html, body, [class*="st-"] {
                font-family: 'Nunito', sans-serif;
            }

            /* Main container */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            /* Board styles */
            .connect4-board {
                background-color: #0077B6;
                border-radius: 15px;
                padding: 15px;
                display: inline-block;
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                border: 5px solid #023E8A;
            }
            .connect4-row {
                display: flex;
            }
            .connect4-cell {
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 45px;
                background-color: #CAF0F8;
                margin: 5px;
                border-radius: 50%;
                box-shadow: inset 0 4px 6px rgba(0,0,0,0.4);
            }

            /* Action buttons above the board */
            .action-buttons {
                margin-bottom: 15px;
            }
            div.stButton > button {
                width: 100%;
                height: 45px;
                font-weight: bold;
                border-radius: 10px;
            }
            div.stButton > button:disabled {
                background-color: #e0e0e0;
                color: #a0a0a0;
                border-color: #c0c0c0;
            }

            /* Game status header */
            .game-status {
                font-size: 1.75rem;
                font-weight: 700;
                text-align: center;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 20px;
                color: white;
            }
            .status-turn { background-color: #6096BA; }
            .status-win { background-color: #4CAF50; }
            .status-draw { background-color: #FFA500; }

            /* Game Over container */
            .game-over-container {
                text-align: center;
                margin-top: 25px;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Main Application Logic (Improved) ---

def initialize_session_state():
    """Initializes session state keys if they don't exist."""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = None

def render_game_setup():
    """Renders the initial screen to select the opponent."""
    st.subheader("Choose Your Opponent")
    cols = st.columns([1, 1])
    if cols[0].button("👤 Play vs. Human", use_container_width=True):
        st.session_state.game_state = create_game("human")
        st.rerun()
    if cols[1].button("🤖 Play vs. Computer", use_container_width=True):
        st.session_state.game_state = create_game("computer")
        st.rerun()

def render_game_interface():
    """Renders the main game board, controls, and status."""
    game = st.session_state.game_state
    
    # Check if it's the computer's turn and make a move
    is_computer_turn = (
        game.get('opponent_type') == 'computer' and
        game['current_player'] == 2 and
        not game['game_over']
    )
    if is_computer_turn:
        with st.spinner("🤖 Computer is thinking..."):
            time.sleep(0.7) # A more noticeable delay for the AI
            # The computer is always player 2, making a move for itself
            new_state = make_move(game['game_id'], 2, -1) # col is ignored for computer
            if new_state:
                st.session_state.game_state = new_state
            st.rerun()

    # --- Sidebar for in-game controls ---
    with st.sidebar:
        st.header("🎮 Game Controls")
        if st.button("Start New Game"):
            st.session_state.game_state = None
            st.rerun()
        if game:
            st.write(f"**Game ID:** `{game['game_id']}`")
            st.write(f"**Opponent:** {game.get('opponent_type', 'N/A').capitalize()}")

    # --- Main Game Display ---
    render_status_header(game)

    # Action buttons for dropping pieces
    is_player_turn = not is_computer_turn and not game['game_over']
    cols = st.columns(7)
    for i in range(7):
        if cols[i].button(f"👇", key=f"col_{i}", help=f"Drop piece in column {i+1}", disabled=not is_player_turn):
            player = game['current_player']
            new_state = make_move(game['game_id'], player, i)
            if new_state:
                st.session_state.game_state = new_state
            st.rerun()

    # Render the board
    render_board(game['board'])

    # Render game over options
    if game['game_over']:
        st.markdown("<div class='game-over-container'></div>", unsafe_allow_html=True)
        st.balloons()
        if st.button("🎈 Play Again?", use_container_width=True):
            st.session_state.game_state = None
            st.rerun()

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="centered")
    inject_custom_css()
    st.title(f"{PAGE_ICON} Connect 4")

    initialize_session_state()

    if not st.session_state.game_state:
        render_game_setup()
    else:
        render_game_interface()

if __name__ == "__main__":
    main()