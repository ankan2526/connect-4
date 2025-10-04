# app.py

import streamlit as st
import requests
import time

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/games"
PIECE_EMOJI = {0: "⚪", 1: "🔴", 2: "🟡"}
PAGE_TITLE = "Connect 4"
PAGE_ICON = "🕹️"

# --- API Helper Functions ---

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
            st.warning(response.json().get('detail', 'Invalid move!'))
            return st.session_state.game_state # Return current state on bad move
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the game server: {e}")
        return None

# --- UI Rendering Functions ---

def render_board(board: list):
    """Renders the game board with emojis and custom styling."""
    board_html = "<div class='connect4-board'>"
    for row in board:
        board_html += "<div class='connect4-row'>"
        for cell in row:
            board_html += f"<div class='connect4-cell'>{PIECE_EMOJI.get(cell, ' ')}</div>"
        board_html += "</div>"
    board_html += "</div>"
    st.markdown(board_html, unsafe_allow_html=True)

def display_game_status(game: dict):
    """Displays the current turn or the winner."""
    if game['game_over']:
        if game['winner'] == 'draw':
            st.info("🤝 It's a Draw!", icon="🤝")
        else:
            winner_emoji = PIECE_EMOJI.get(game['winner'], '')
            st.success(f"🎉 Player {game['winner']} ({winner_emoji}) Wins! 🎉", icon="🎉")
    else:
        player_emoji = PIECE_EMOJI.get(game['current_player'], '')
        st.info(f"Turn: Player {game['current_player']} ({player_emoji})", icon="⏳")

def inject_custom_css():
    """Injects CSS for a better-looking board and UI elements."""
    st.markdown("""
        <style>
            .connect4-board {
                background-color: #0077B6; /* A nice blue */
                border-radius: 10px;
                padding: 10px;
                display: inline-block;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .connect4-row {
                display: flex;
            }
            .connect4-cell {
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 35px;
                background-color: #CAF0F8; /* Light blue for empty slots */
                margin: 4px;
                border-radius: 50%;
                box-shadow: inset 0 3px 5px rgba(0,0,0,0.3);
            }
            div.stButton > button {
                width: 100%;
                height: 40px;
                margin: 2px 0;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Main Application Logic ---

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="centered")
    inject_custom_css()
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")

    # --- Sidebar for Game Controls ---
    with st.sidebar:
        st.header("🎮 Game Controls")
        if st.button("Start New Game vs. Human"):
            st.session_state.game_state = create_game("human")
        if st.button("Start New Game vs. Computer"):
            st.session_state.game_state = create_game("computer")

        if 'game_state' in st.session_state and st.session_state.game_state:
            st.write(f"**Game ID:** `{st.session_state.game_state['game_id']}`")


    # --- Main Game Display ---
    if 'game_state' not in st.session_state or not st.session_state.game_state:
        st.info("Start a new game from the sidebar to begin!")
        return

    game = st.session_state.game_state
    
    # Display status and board
    display_game_status(game)
    render_board(game['board'])
    
    # Display move buttons only if the game is not over
    if not game['game_over']:
        cols = st.columns(7)
        for i, col in enumerate(cols):
            if col.button(f"Drop {i+1}", key=f"col_{i}"):
                player = game['current_player']
                new_state = make_move(game['game_id'], player, i)
                if new_state:
                    st.session_state.game_state = new_state
                    # Brief pause for computer move to feel more natural
                    if new_state.get('opponent_type') == 'computer' and not new_state.get('game_over'):
                        time.sleep(0.5)
                    st.rerun() # Use st.rerun() for a cleaner refresh

if __name__ == "__main__":
    main()