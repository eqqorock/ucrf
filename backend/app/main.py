from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from pydantic import BaseModel
from typing import List
import joblib
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import re
import json

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

# Allow preview Vercel subdomains by default during development. Override with VITE_ALLOW_ORIGIN_REGEX in Render env if needed.
raw_allow_origin_regex = os.environ.get("VITE_ALLOW_ORIGIN_REGEX")
if raw_allow_origin_regex is None:
    # permissive default for vercel preview domains (dev only)
    allow_origin_regex = r"https://.*\.vercel\.app"
else:
    allow_origin_regex = raw_allow_origin_regex or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Fallback middleware: ensure CORS headers are present on responses when origin matches.
# This is a safety net for preview domains and errors that may bypass the built-in CORS middleware.
# Keep this permissive only for development; remove or tighten for production.
_allow_origin_regex_compiled = None
if allow_origin_regex:
    try:
        _allow_origin_regex_compiled = re.compile(allow_origin_regex)
    except Exception:
        _allow_origin_regex_compiled = None


@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    origin = request.headers.get("origin")
    response = await call_next(request)
    try:
        matched = False
        if origin:
            if origin in allowed_origins:
                matched = True
            elif _allow_origin_regex_compiled and _allow_origin_regex_compiled.match(origin):
                matched = True
        if matched:
            # Mirror back the request origin (safer than using *)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            if allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            # Allow common headers/methods for preflighted requests
            response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            response.headers.setdefault("Access-Control-Allow-Headers", "*")
    except Exception:
        # Don't let header injection break the response
        pass
    return response

# Logging and model caching: load models once at startup to avoid joblib.load on every request.
import logging
logger = logging.getLogger("ucrf")
logging.basicConfig(level=logging.INFO)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
CLF_PATH = os.path.join(MODEL_DIR, "reliability_clf.joblib")
REG_PATH = os.path.join(MODEL_DIR, "cost_reg.joblib")

_clf = None
_reg = None

def try_load_models():
    global _clf, _reg
    try:
        if os.path.exists(CLF_PATH) and os.path.exists(REG_PATH):
            _clf = joblib.load(CLF_PATH)
            _reg = joblib.load(REG_PATH)
            logger.info(f"Loaded models from {MODEL_DIR}")
        else:
            logger.info(f"Model files not found in {MODEL_DIR}")
    except Exception as e:
        logger.exception("Failed to load models: %s", e)

# Run at import/startup
logger.info(f"Allowed CORS origins: {allowed_origins}, allow_credentials={allow_credentials}")
try_load_models()


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
    v = models.Vehicle(**payload.model_dump())
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
    # Use cached models when available to reduce latency.
    try:
        if _clf is not None and _reg is not None:
            # Attempt to construct input matching the trained model.
            # If the model has feature names, create a DataFrame and populate likely columns.
            if hasattr(_clf, "feature_names_in_"):
                # Lazy import pandas only when needed; if missing, fall back to placeholder
                try:
                    import pandas as pd
                except Exception:
                    logger.warning("pandas not available in environment; returning placeholder prediction")
                    return ForecastOut(predicted_issue=str(_clf.predict([[2025 - year]])[0]) if hasattr(_clf, 'predict') else "unknown", likelihood=0.5, estimated_cost=0.0, range_months=6)
                cols = list(_clf.feature_names_in_)
                row = {c: 0 for c in cols}
                for c in cols:
                    lc = c.lower()
                    if "mile" in lc:
                        row[c] = mileage
                    elif "age" in lc or "vehicle_age" in lc:
                        row[c] = 2025 - year
                    elif lc == "year" or ("year" in lc and "age" not in lc):
                        row[c] = year
                    elif "make" in lc:
                        row[c] = make
                    elif "model" in lc:
                        row[c] = model_name
                X_df = pd.DataFrame([row], columns=cols)
                risk = _clf.predict(X_df)[0]
                est_cost = float(_reg.predict(X_df)[0])
            else:
                # Fall back to using n_features_in_ if available, padding zeros for missing features.
                try:
                    import numpy as np
                except Exception:
                    logger.warning("numpy not available in environment; returning placeholder prediction")
                    return ForecastOut(predicted_issue="unknown", likelihood=0.1, estimated_cost=0.0, range_months=6)
                n = getattr(_clf, "n_features_in_", None) or getattr(_clf, "n_features_in", None) or 2
                X = np.zeros((1, int(n)))
                X[0, 0] = 2025 - year
                if int(n) > 1:
                    X[0, 1] = mileage
                risk = _clf.predict(X)[0]
                est_cost = float(_reg.predict(X)[0])
            return ForecastOut(predicted_issue=str(risk), likelihood=0.5, estimated_cost=est_cost, range_months=6)
        else:
            logger.info("Models not loaded; returning placeholder prediction")
            return ForecastOut(predicted_issue="unknown", likelihood=0.1, estimated_cost=0.0, range_months=6)
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="Prediction error")


@app.get("/health", response_model=dict)
def health():
    """Lightweight health endpoint showing CORS and model status."""
    clf_features = None
    try:
        if _clf is not None and hasattr(_clf, "feature_names_in_"):
            clf_features = list(_clf.feature_names_in_)
    except Exception:
        clf_features = None
    return {
        "ok": True,
        "allowed_origins": allowed_origins,
        "models_loaded": _clf is not None and _reg is not None,
        "clf_n_features": getattr(_clf, "n_features_in_", None),
        "clf_feature_names": clf_features,
    }


@app.get("/problem-catalog", response_model=dict)
def problem_catalog():
    """Return the problem catalog JSON file. This keeps the frontend in sync with the backend's taxonomy.

    Falls back to a simple structure if the file cannot be read.

    """
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "problem_catalog.json")
    try:
        with open(data_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Problem catalog not found")
    except Exception as e:
        logger.exception("Failed to read problem catalog: %s", e)
        raise HTTPException(status_code=500, detail="Failed to load catalog")
