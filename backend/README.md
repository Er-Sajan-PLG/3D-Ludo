# 3D Ludo Python Backend

This folder contains a simple FastAPI backend that exposes the existing Python game engine.

## Run locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Access:
   - `GET http://localhost:8000/api/game`
   - `POST http://localhost:8000/api/game` with JSON `{ "action": "play_turn" }`

## Notes

- This backend uses the game engine stored in `engine/`.
- CORS is enabled for common local frontend origins.
