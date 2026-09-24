from pydantic import BaseModel, Field
from typing import Optional

class Place(BaseModel):
    name: str
    lat: float
    lon: float
    visit_minutes: int = Field(ge=15, le=600)
    cost: int = Field(ge=0, le=100000)

class PlanRequest(BaseModel):
    title: str = "My Day Trip"
    trip_date: str
    start_time: str
    end_time: str
    budget: int = Field(ge=0, le=1000000)
    start: Place
    places: list[Place]

class PlanResponse(BaseModel):
    title: str
    trip_date: str
    start_time: str
    end_time: str
    budget: int
    start: Place
    total_cost: int
    total_minutes: int
    places: list[dict]
    skipped: list[dict]
    weather: list[dict]
    summary: str
