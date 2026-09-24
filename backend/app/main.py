from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import Base, SessionLocal, engine
from .models import Itinerary
from .planner import build_plan
from .schemas import PlanRequest, PlanResponse
from .services import make_summary, weather_for, search_places

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Day Planner")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/search")
async def search(q: str = Query(min_length=2)):
    return await search_places(q)

@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest, session: Session = Depends(db)):
    try:
        places, skipped, total_minutes, total_cost = build_plan(req)
    except ValueError as e:
        raise HTTPException(400, str(e))

    weather = []
    for p in places:
        try:
            value = await weather_for(p["lat"], p["lon"], req.trip_date)
        except Exception:
            value = {"temperature_max": None, "temperature_min": None, "rain_probability": None, "weather_code": None}
        weather.append({"name": p["name"], **value})

    summary = await make_summary(req.title, req.trip_date, places, total_cost, total_minutes, weather)
    return {
        "title": req.title,
        "trip_date": req.trip_date,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "budget": req.budget,
        "start": req.start,
        "total_cost": total_cost,
        "total_minutes": total_minutes,
        "places": places,
        "skipped": [p.model_dump() for p in skipped],
        "weather": weather,
        "summary": summary,
    }

@app.post("/api/itineraries")
def save_plan(plan: PlanResponse, session: Session = Depends(db)):
    item = Itinerary(
        title=plan.title, trip_date=plan.trip_date, start_time=plan.start_time, end_time=plan.end_time,
        budget=plan.budget, start=plan.start.model_dump(), places=plan.places, weather=plan.weather, created_at=datetime.utcnow()
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return {"id": item.id, "title": item.title}

@app.get("/api/itineraries")
def get_itineraries(session: Session = Depends(db)):
    rows = session.query(Itinerary).order_by(Itinerary.id.desc()).all()
    return [
        {"id": x.id, "title": x.title, "trip_date": x.trip_date, "total_places": len(x.places or [])}
        for x in rows
    ]

@app.get("/api/itineraries/{item_id}")
def get_itinerary(item_id: int, session: Session = Depends(db)):
    item = session.get(Itinerary, item_id)
    if not item:
        raise HTTPException(404, "Itinerary not found")
    return {
        "id": item.id, "title": item.title, "trip_date": item.trip_date, "start_time": item.start_time,
        "end_time": item.end_time, "budget": item.budget, "start": item.start, "places": item.places, "weather": item.weather
    }
