"""Data ingestion and preprocessing pipeline.

This module provides functions to ingest CSVs or APIs, clean and normalize data,
engineer features and persist processed rows to the database.

Functions:
 - load_csv
 - fetch_nhtsa_dummy (placeholder for API ingestion)
 - clean_and_merge
 - engineer_features
 - save_to_db
"""
from typing import List
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from . import models


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame; basic parsing helpers."""
    return pd.read_csv(path)


def fetch_nhtsa_dummy() -> pd.DataFrame:
    """Placeholder: in production, call NHTSA APIs and normalize results."""
    # For now return an empty DataFrame with expected columns
    return pd.DataFrame(columns=["make", "model", "year", "complaints"])


def clean_and_merge(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Normalize column names, drop duplicates and merge on make/model/year."""
    normed = []
    for df in dfs:
        tmp = df.copy()
        tmp.columns = [c.strip().lower() for c in tmp.columns]
        # rename common columns
        if "manufacturer" in tmp.columns:
            tmp = tmp.rename(columns={"manufacturer": "make"})
        normed.append(tmp)
    if not normed:
        return pd.DataFrame()
    merged = pd.concat(normed, ignore_index=True, sort=False)
    merged = merged.drop_duplicates(subset=["make", "model", "year"])
    return merged


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add vehicle_age, complaint_rate (if available), recall_count placeholder, avg_service_cost placeholder."""
    out = df.copy()
    current_year = datetime.now().year
    out["vehicle_age"] = current_year - out["year"].astype(int)
    out["complaint_rate"] = out.get("complaints", 0).fillna(0).astype(float)
    out["recall_count"] = out.get("recalls", 0).fillna(0).astype(int)
    out["avg_service_cost"] = out.get("avg_service_cost", 0).fillna(0).astype(float)
    return out


def save_to_db(df: pd.DataFrame, db: Session):
    """Persist vehicles and service summaries to the DB; idempotent-ish."""
    for _, row in df.iterrows():
        # upsert vehicle by make/model/year
        v = db.query(models.Vehicle).filter_by(make=row.get("make"), model=row.get("model"), year=int(row.get("year"))).first()
        if not v:
            v = models.Vehicle(
                make=row.get("make"), model=row.get("model"), year=int(row.get("year")), mileage=int(row.get("mileage", 0)), engine_type=row.get("engine_type"), transmission=row.get("transmission")
            )
            db.add(v)
            db.commit()
            db.refresh(v)
        # optionally add a service history summary row
        if row.get("avg_service_cost"):
            sh = models.ServiceHistory(vehicle_id=v.id, service_date=datetime.now().date(), service_type="summary", cost=float(row.get("avg_service_cost")))
            db.add(sh)
            db.commit()
