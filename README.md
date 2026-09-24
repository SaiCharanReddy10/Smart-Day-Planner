# Smart Day Planner

A small full-stack day-trip planner built to practice FastAPI, React, PostgreSQL, Leaflet, Open-Meteo, Docker and a local Ollama model.

## Features

- Search places with OpenStreetMap Nominatim
- Show the selected route with Leaflet and OpenStreetMap tiles
- Select a start point and day-trip stops
- Set available time and budget
- Build a simple route using Haversine distance
- Fetch weather from Open-Meteo
- Generate a short optional summary with local Ollama
- Save itineraries in PostgreSQL
- View the route on a Leaflet map

## Run with Docker

Make sure Ollama is running on the host and the model exists:

```bash
ollama pull qwen2.5:7b
docker compose up --build
```

Open `http://localhost:5173`.

Ollama is optional. If it is unavailable, the app uses a normal Python fallback summary.

## Without Docker

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `DATABASE_URL` to a local PostgreSQL database when running outside Docker.
