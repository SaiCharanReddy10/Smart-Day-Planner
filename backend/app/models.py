from sqlalchemy import Column, DateTime, Integer, String, JSON
from .database import Base

class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    trip_date = Column(String(20), nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    budget = Column(Integer, nullable=False)
    start = Column(JSON, nullable=False)
    places = Column(JSON, nullable=False)
    weather = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
