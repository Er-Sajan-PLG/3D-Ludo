"""FastAPI backend for 3D Ludo.

This module exposes game state and turn actions through a lightweight API
that uses the existing engine game controller.
"""

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.utils import GameConfig
from engine.game import Game, GameState

app = FastAPI(
    title="3D Ludo Python Backend",
    description="FastAPI backend service for the 3D Ludo game engine.",
    version="0.1.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameAction(BaseModel):
    action: str


def _create_game() -> Game:
    config = GameConfig().config
    config['require_login'] = False
    game = Game(config)
    initialized = game.initialize_game()
    if not initialized:
        raise RuntimeError("Failed to initialize 3D Ludo game backend")
    return game


backend_game = _create_game()


def _serialize_game(game: Game) -> dict:
    current_player = game.current_player
    winner = game.winner
    message = ""

    if game.state == GameState.FINISHED:
        message = f"Game finished. Winner: {winner.name if winner else 'Unknown'}"
    elif current_player:
        if game.dice.last_roll is not None:
            message = f"{current_player.name} rolled a {game.dice.last_roll}."
        else:
            message = f"{current_player.name} is ready to move."
    else:
        message = "Game is initializing."

    return {
        "state": game.state.value,
        "turn_number": game.current_turn,
        "current_player": {
            "player_id": current_player.player_id if current_player else None,
            "name": current_player.name if current_player else None,
        },
        "winner": {
            "player_id": winner.player_id,
            "name": winner.name,
        } if winner else None,
        "dice": game.dice.to_dict(),
        "players": [player.to_dict() for player in game.players],
        "pieces": game.pieces.to_dict(),
        "board": game.board.to_dict(),
        "message": message,
    }


@app.get("/api/game")
def get_game_state() -> dict:
    """Return the current game state."""
    return _serialize_game(backend_game)


@app.post("/api/game")
def perform_game_action(action: GameAction = Body(...)) -> dict:
    """Perform a game action such as rolling a turn."""
    global backend_game

    if action.action == "play_turn":
        if backend_game.state == GameState.FINISHED:
            raise HTTPException(status_code=400, detail="Game has already finished")

        backend_game.process_turn()
        return _serialize_game(backend_game)

    if action.action == "reset":
        backend_game = _create_game()
        return _serialize_game(backend_game)

    raise HTTPException(status_code=400, detail=f"Unknown action: {action.action}")
