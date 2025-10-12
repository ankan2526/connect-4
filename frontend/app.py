# app.py

import streamlit as st
import requests
import time
from typing import Dict, Any, Optional

# --- Configuration ---
# Grouping constants makes them easier to manage.
class Cfg:
    API_URL = "http://127.0.0.1:8000/games"
    PIECE_EMOJI = {0: "⚪", 1: "🔴", 2: "🟡"}
    PAGE_TITLE = "Connect 4"
    PAGE_ICON = "🕹️"

# --- API Client ---
# Encapsulating API logic into a class improves organization and reusability.
class GameAPIClient:
    """Handles all communication with the backend game server."""

    def __init__(self, base_url: str):
        """Initializes the client with the server's base URL."""
        self.base_url = base_url

    def create_game(self, opponent_type: str) -> Optional[Dict[str, Any]]:
        """Requests the server to create a new game."""
        try:
            response = requests.post(self.base_url, json={"opponent_type": opponent_type})
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the game server: {e}")
            return None

    def make_move(self, game_id: str, player: int, col: int) -> Optional[Dict[str, Any]]:
        """Sends a player's move to the server."""
        try:
            url = f"{self.base_url}/{game_id}/move"
            response = requests.post(url, json={"player": player, "col": col})
            if response.status_code == 400:
                st.toast("That column is full!", icon="⚠️")
                return st.session_state.game  # Return current state on a bad move
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the game server: {e}")
            return None

# --- UI Rendering Functions ---
# These functions are now focused solely on displaying Streamlit components.

def inject_custom_css():
    """Injects CSS for a modern game UI. (No changes from original)"""
    st.markdown("""
        <style>
            /* CSS styles are unchanged, but kept in a dedicated function */
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
            html, body, [class*="st-"] { font-family: 'Nunito', sans-serif; }
            .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
            .connect4-board { background-color: #0077B6; border-radius: 15px; padding: 15px; display: inline-block; box-shadow: 0 8px 16px rgba(0,0,0,0.3); border: 5px solid #023E8A; }
            .connect4-row { display: flex; }
            .connect4-cell { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 45px; background-color: #CAF0F8; margin: 5px; border-radius: 50%; box-shadow: inset 0 4px 6px rgba(0,0,0,0.4); }
            .action-buttons { margin-bottom: 15px; }
            div.stButton > button { width: 100%; height: 45px; font-weight: bold; border-radius: 10px; }
            div.stButton > button:disabled { background-color: #e0e0e0; color: #a0a0a0; border-color: #c0c0c0; }
            .game-status { font-size: 1.75rem; font-weight: 700; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px; color: white; }
            .status-turn { background-color: #6096BA; }
            .status-win { background-color: #4CAF50; }
            .status-draw { background-color: #FFA500; }
            .game-over-container { text-align: center; margin-top: 25px; }
        </style>
    """, unsafe_allow_html=True)

def render_board(board: list):
    """Renders the game board using HTML for custom styling."""
    board_html = "<div class='connect4-board'>"
    for row in board:
        board_html += "<div class='connect4-row'>"
        for cell in row:
            board_html += f"<div class='connect4-cell'>{Cfg.PIECE_EMOJI.get(cell, '')}</div>"
        board_html += "</div>"
    board_html += "</div>"
    st.markdown(board_html, unsafe_allow_html=True)

def render_status_header(game: dict):
    """Displays the current turn or the winner."""
    if game['game_over']:
        if game['winner'] == 'draw':
            st.markdown("<div class='game-status status-draw'>🤝 It's a Draw! 🤝</div>", unsafe_allow_html=True)
        else:
            winner_emoji = Cfg.PIECE_EMOJI.get(game['winner'], '')
            st.markdown(f"<div class='game-status status-win'>🎉 Player {game['winner']} ({winner_emoji}) Wins! 🎉</div>", unsafe_allow_html=True)
    else:
        player_emoji = Cfg.PIECE_EMOJI.get(game['current_player'], '')
        st.markdown(f"<div class='game-status status-turn'>Turn: Player {game['current_player']} ({player_emoji})</div>", unsafe_allow_html=True)

def render_action_buttons(game: dict, api_client: GameAPIClient):
    """Renders the column buttons for the player to make a move."""
    is_player_turn = (
        game.get('opponent_type') != 'computer' or
        game['current_player'] == 1
    ) and not game['game_over']

    cols = st.columns(7)
    for i in range(7):
        if cols[i].button(f"👇", key=f"col_{i}", help=f"Drop piece in column {i+1}", disabled=not is_player_turn):
            player = game['current_player']
            new_state = api_client.make_move(game['game_id'], player, i)
            if new_state:
                st.session_state.game = new_state
                st.rerun()

def render_sidebar(game: Optional[dict]):
    """Renders the sidebar with game controls and information."""
    with st.sidebar:
        st.header("🎮 Game Controls")
        if st.button("Start New Game"):
            st.session_state.game = None
            st.rerun()
        if game:
            st.write(f"**Game ID:** `{game['game_id']}`")
            st.write(f"**Opponent:** {game.get('opponent_type', 'N/A').capitalize()}")

# --- Application Logic ---
# The main flow of the application is controlled here.

def initialize_session_state():
    """Initializes `st.session_state.game` if it doesn't exist."""
    if 'game' not in st.session_state:
        st.session_state.game = None

def handle_opponent_selection(api_client: GameAPIClient):
    """Displays the opponent selection screen."""
    st.subheader("Choose Your Opponent")
    cols = st.columns([1, 1])
    if cols[0].button("👤 Play vs. Human", use_container_width=True):
        st.session_state.game = api_client.create_game("human")
        st.rerun()
    if cols[1].button("🤖 Play vs. Computer", use_container_width=True):
        st.session_state.game = api_client.create_game("computer")
        st.rerun()

def handle_computer_turn(game: dict, api_client: GameAPIClient):
    """Checks for and executes the computer's turn, if applicable."""
    is_computer_turn = (
        game.get('opponent_type') == 'computer' and
        game['current_player'] == 2 and not game['game_over']
    )
    if is_computer_turn:
        with st.spinner("🤖 Computer is thinking..."):
            time.sleep(0.7)  # Artificial delay for better UX
            # For the computer, player is always 2 and column is ignored by the backend.
            new_state = api_client.make_move(game['game_id'], 2, -1)
            if new_state:
                st.session_state.game = new_state
            st.rerun()

def play_game(api_client: GameAPIClient):
    """Controls the rendering of the active game interface."""
    game = st.session_state.game

    render_sidebar(game)
    render_status_header(game)

    # First, check if it's the computer's turn and let it play.
    # The `handle_computer_turn` will trigger a rerun, stopping this script.
    handle_computer_turn(game, api_client)

    # If it's not the computer's turn, render the player action buttons.
    render_action_buttons(game, api_client)

    render_board(game['board'])

    # If the game is over, show a success message and a "Play Again" button.
    if game['game_over']:
        st.balloons()
        if st.button("🎈 Play Again?", use_container_width=True):
            st.session_state.game = None
            st.rerun()

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title=Cfg.PAGE_TITLE, page_icon=Cfg.PAGE_ICON, layout="centered")
    inject_custom_css()
    st.title(f"{Cfg.PAGE_ICON} Connect 4")

    # Initialize state and API client
    initialize_session_state()
    api_client = GameAPIClient(Cfg.API_URL)

    # Simple router: show setup screen or active game screen
    if st.session_state.game is None:
        handle_opponent_selection(api_client)
    else:
        play_game(api_client)

if __name__ == "__main__":
    main()