import React, { useState } from "react";
import { CircleMarker, MapContainer, Popup, Polyline, TileLayer } from "react-leaflet";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function searchPlace(q) {
  const r = await fetch(`${API}/api/search?q=${encodeURIComponent(q)}`);
  return r.ok ? r.json() : [];
}

function PlaceSearch({ label, onPick }) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const search = async () => setResults(await searchPlace(q));
  return <div className="search"><label>{label}</label><div className="row"><input value={q} onChange={e => setQ(e.target.value)} placeholder="Search a place"/><button onClick={search}>Search</button></div>{results.map(x => <button className="result" key={x.place_id} onClick={() => { onPick(x); setResults([]); setQ(x.display_name); }}>{x.display_name}</button>)}</div>;
}

function App() {
  const today = new Date().toISOString().slice(0, 10);
  const [start, setStart] = useState(null);
  const [places, setPlaces] = useState([]);
  const [date, setDate] = useState(today);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("18:00");
  const [budget, setBudget] = useState(1500);
  const [title, setTitle] = useState("My Day Trip");
  const [plan, setPlan] = useState(null);
  const [saved, setSaved] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const pickStart = x => setStart({ name: x.display_name.split(",")[0], lat: +x.lat, lon: +x.lon, visit_minutes: 0, cost: 0 });
  const addPlace = x => setPlaces([...places, { name: x.display_name.split(",")[0], lat: +x.lat, lon: +x.lon, visit_minutes: 60, cost: 200 }]);

  const createPlan = async () => {
    if (!start || !places.length) return setError("Choose a start location and at least one place.");
    setLoading(true); setError("");
    try {
      const r = await fetch(`${API}/api/plan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, trip_date: date, start_time: startTime, end_time: endTime, budget: +budget, start, places }) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Could not create plan");
      setPlan(data);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const savePlan = async () => {
    await fetch(`${API}/api/itineraries`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(plan) });
    loadSaved();
  };

  const loadSaved = async () => {
    const r = await fetch(`${API}/api/itineraries`);
    setSaved(await r.json());
  };

  const path = plan?.places?.length ? [[start.lat, start.lon], ...plan.places.map(x => [x.lat, x.lon])] : start ? [[start.lat, start.lon]] : [];

  return <main>
    <header><div><h1>Smart Day Planner</h1><p>Plan a simple day trip around time, budget and weather.</p></div><button onClick={loadSaved}>Saved Trips</button></header>
    <section className="grid">
      <div className="card">
        <h2>Trip details</h2>
        <label>Title<input value={title} onChange={e => setTitle(e.target.value)} /></label>
        <div className="two"><label>Date<input type="date" value={date} onChange={e => setDate(e.target.value)} /></label><label>Budget<input type="number" value={budget} onChange={e => setBudget(e.target.value)} /></label></div>
        <div className="two"><label>From<input type="time" value={startTime} onChange={e => setStartTime(e.target.value)} /></label><label>To<input type="time" value={endTime} onChange={e => setEndTime(e.target.value)} /></label></div>
        <PlaceSearch label="Start location" onPick={pickStart} />
        {start && <div className="picked">Start: {start.name}</div>}
        <PlaceSearch label="Add places" onPick={addPlace} />
        <div className="places">{places.map((p, i) => <div className="place" key={`${p.name}-${i}`}><div><b>{p.name}</b><small>{p.visit_minutes} min · ₹{p.cost}</small></div><button onClick={() => setPlaces(places.filter((_, j) => i !== j))}>×</button></div>)}</div>
        <button className="primary" onClick={createPlan}>{loading ? "Planning..." : "Create Itinerary"}</button>
        {error && <p className="error">{error}</p>}
      </div>
      <div className="card map-card">{start ? <MapContainer center={[start.lat, start.lon]} zoom={12} scrollWheelZoom><TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />{start && <CircleMarker center={[start.lat, start.lon]} radius={8}><Popup>Start</Popup></CircleMarker>}{plan?.places?.map(p => <CircleMarker key={p.name} center={[p.lat, p.lon]} radius={7}><Popup>{p.name}</Popup></CircleMarker>)}{path.length > 1 && <Polyline positions={path} />}</MapContainer> : <div className="empty">Pick a start location to see the map.</div>}</div>
    </section>
    {plan && <section className="result-grid">
      <div className="card"><div className="result-head"><h2>{plan.title}</h2><button onClick={savePlan}>Save</button></div><p>{plan.summary}</p><div className="stats"><span>₹{plan.total_cost}<small>estimated cost</small></span><span>{plan.total_minutes} min<small>planned time</small></span><span>{plan.places.length}<small>stops</small></span></div>{plan.places.map((p, i) => <div className="stop" key={p.name}><b>{i + 1}. {p.name}</b><span>{p.travel_minutes} min travel · {p.visit_minutes} min visit · ₹{p.cost}</span></div>)}{plan.skipped.length > 0 && <p className="muted">Not included: {plan.skipped.map(x => x.name).join(", ")}</p>}</div>
      <div className="card"><h2>Weather</h2>{plan.weather.map(w => <div className="weather" key={w.name}><div><b>{w.name}</b><span>{w.temperature_min ?? "-"}° to {w.temperature_max ?? "-"}°</span></div><span>{w.rain_probability ?? "-"}% rain</span></div>)}</div>
    </section>}
    {saved.length > 0 && <section className="card saved"><h2>Saved trips</h2>{saved.map(x => <div key={x.id}><b>{x.title}</b><span>{x.trip_date} · {x.total_places} stops</span></div>)}</section>}
  </main>;
}

export default App;
