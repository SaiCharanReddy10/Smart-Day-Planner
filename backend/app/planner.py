from math import radians, sin, cos, asin, sqrt
from datetime import datetime


def haversine(a_lat, a_lon, b_lat, b_lon):
    lat1, lon1, lat2, lon2 = map(radians, [a_lat, a_lon, b_lat, b_lon])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(x))


def minutes_between(start, end):
    a = datetime.strptime(start, "%H:%M")
    b = datetime.strptime(end, "%H:%M")
    if b <= a:
        raise ValueError("End time must be after start time")
    return int((b - a).total_seconds() // 60)


def build_plan(req):
    available = minutes_between(req.start_time, req.end_time)
    current = req.start
    total_minutes, total_cost = 0, 0
    selected, skipped = [], []
    remaining = list(req.places)

    while remaining:
        remaining.sort(key=lambda p: haversine(current.lat, current.lon, p.lat, p.lon))
        chosen = None
        for p in remaining:
            travel = max(5, round(haversine(current.lat, current.lon, p.lat, p.lon) / 30 * 60))
            needed = travel + p.visit_minutes
            if total_minutes + needed <= available and total_cost + p.cost <= req.budget:
                chosen = (p, travel)
                break
        if not chosen:
            skipped.extend(remaining)
            break
        p, travel = chosen
        total_minutes += travel + p.visit_minutes
        total_cost += p.cost
        selected.append({
            "name": p.name,
            "lat": p.lat,
            "lon": p.lon,
            "visit_minutes": p.visit_minutes,
            "cost": p.cost,
            "travel_minutes": travel,
        })
        current = p
        remaining.remove(p)

    return selected, skipped, total_minutes, total_cost
