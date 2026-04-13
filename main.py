from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.orchestrator import run

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    location: str
    weather: str = "clear"
    time: str | None = None
    simulation_minutes: int = 0

@app.get("/")
def home():
    return {"message": "AI City Brain API running"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    query = f"{req.weather} at {req.time or 'now'} in {req.location}"
    return run(query)