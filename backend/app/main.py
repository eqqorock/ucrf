from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from pydantic import BaseModel
from typing import List
import joblib
import os
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UCRF - Vehicle Reliability Forecast")

# CORS: allow Vercel frontend origin (replace with your actual Vercel domain or use ['*'] for testing)
# Configure CORS origins via environment variable. Accept a single origin or a comma-separated list.
raw_origins = os.environ.get("VITE_ALLOWED_ORIGINS") or os.environ.get("VITE_APP_ORIGIN")
if raw_origins:
    allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
else:
    # default to the frontend production domain; change this in Render env if your Vercel domain differs
    allowed_origins = ["https://ucrf.vercel.app"]

# If allowed_origins contains the wildcard, disable credentials (browsers reject wildcard + credentials).
allow_credentials = True
if "*" in allowed_origins:
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    mileage: int = 0
    engine_type: str | None = None
    transmission: str | None = None


class ForecastOut(BaseModel):
    predicted_issue: str
    likelihood: float
    estimated_cost: float
    range_months: int


@app.post("/vehicles", response_model=dict)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    v = models.Vehicle(**payload.dict())
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"id": v.id}


@app.get("/vehicles", response_model=List[dict])
def list_vehicles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    vs = db.query(models.Vehicle).offset(skip).limit(limit).all()
    return [{"id": v.id, "make": v.make, "model": v.model, "year": v.year} for v in vs]


@app.get("/service-history", response_model=List[dict])
def get_service_history(vehicle_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.ServiceHistory)
    if vehicle_id:
        q = q.filter(models.ServiceHistory.vehicle_id == vehicle_id)
    items = q.all()
    return [
        {"id": s.id, "vehicle_id": s.vehicle_id, "service_date": s.service_date.isoformat(), "service_type": s.service_type, "cost": s.cost}
        for s in items
    ]


@app.post("/predict", response_model=ForecastOut)
def predict(make: str, model_name: str, year: int, mileage: int = 0):
    # simple fallback predictor: if model exists in /models, load and predict
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "reliability_clf.joblib")
    cost_model_path = os.path.join(os.path.dirname(__file__), "..", "models", "cost_reg.joblib")
    # placeholder behavior
    if os.path.exists(model_path) and os.path.exists(cost_model_path):
        clf = joblib.load(model_path)
        reg = joblib.load(cost_model_path)
        # create a minimal feature vector (this code assumes trained model expects these columns)
        X = [[2025 - year, mileage]]
        risk = clf.predict(X)[0]
        est_cost = float(reg.predict(X)[0])
        return ForecastOut(predicted_issue=str(risk), likelihood=0.5, estimated_cost=est_cost, range_months=6)
    return ForecastOut(predicted_issue="unknown", likelihood=0.1, estimated_cost=0.0, range_months=6)
