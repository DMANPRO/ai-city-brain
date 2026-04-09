import axios from 'axios';

// ── Change this to your FastAPI server IP when testing on device ──
// Use localhost for simulator, your machine's LAN IP for physical device
// e.g. 'http://192.168.1.10:8000'
const BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// ── /analyze ──────────────────────────────────────────────────────
// Main multi-agent pipeline endpoint (Person 2's work)
// POST { location, time, weather, simulation_minutes }
// Returns full agent result with congestion score, incidents, etc.
export async function analyze({ location, time, weather, simulation = 0 }) {
  const payload = { location, weather, simulation_minutes: simulation };
  if (time !== null) payload.time = time;   // null = live TomTom data
  const { data } = await api.post('/analyze', payload);
  return data;
}

// ── /weather ──────────────────────────────────────────────────────
// Auto-fetch weather condition from GPS coords
// GET /weather?lat=12.93&lon=77.62
export async function fetchWeather(lat, lon) {
  const { data } = await api.get('/weather', { params: { lat, lon } });
  return data; // { condition: 'rain' | 'clear' | 'fog' | 'storm' | 'cloudy' }
}

// ── /search ───────────────────────────────────────────────────────
// TomTom Search API — autocomplete Bengaluru locations
// GET /search?q=kora
export async function searchLocations(query) {
  const { data } = await api.get('/search', { params: { q: query } });
  return data; // [{ name, lat, lon }]
}

// ── /hotspots ─────────────────────────────────────────────────────
// Returns top congestion hotspots for map pins
// GET /hotspots
export async function fetchHotspots() {
  const { data } = await api.get('/hotspots');
  return data; // [{ name, lat, lon, score, trend }]
}

// ── /ev-chargers ──────────────────────────────────────────────────
// EV charging stations near a location
// GET /ev-chargers?lat=12.93&lon=77.62
export async function fetchEVChargers(lat, lon) {
  const { data } = await api.get('/ev-chargers', { params: { lat, lon } });
  return data; // [{ name, lat, lon, available }]
}

// ── SSE: /agent-stream ────────────────────────────────────────────
// Server-Sent Events stream for live agent log
// Returns the SSE URL — use EventSource in the component
export function agentStreamURL(location, time, weather) {
  const params = new URLSearchParams({ location, weather });
  if (time !== null) params.set('time', time);
  return `${BASE_URL}/agent-stream?${params.toString()}`;
}

export default api;
