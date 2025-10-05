"""Training workflow: preprocessing, training, evaluation, export.

Usage:
 python train.py --data path/to/processed.csv
"""
from pathlib import Path
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import f1_score, mean_absolute_error
import joblib


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def preprocess(df: pd.DataFrame):
    # simple preprocessing: fillna and select features
    df = df.fillna(0)
    X = df[["vehicle_age", "mileage", "complaint_rate", "recall_count", "avg_service_cost"]]
    # create toy targets if not present
    if "cost" not in df.columns:
        df["cost"] = df["avg_service_cost"]
    if "risk" not in df.columns:
        # risk: High if complaint_rate > median
        df["risk"] = (df["complaint_rate"] > df["complaint_rate"].median()).astype(int)
    y_reg = df["cost"]
    y_clf = df["risk"]
    return X, y_reg, y_clf


def train(X, y_reg, y_clf, out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    X_train, X_test, yreg_train, yreg_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    _, _, yclf_train, yclf_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)

    reg = RandomForestRegressor(n_estimators=50, random_state=42)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)

    reg.fit(X_train, yreg_train)
    clf.fit(X_train, yclf_train)

    yreg_pred = reg.predict(X_test)
    yclf_pred = clf.predict(X_test)

    mae = mean_absolute_error(yreg_test, yreg_pred)
    f1 = f1_score(yclf_test, yclf_pred, average="weighted")

    print(f"MAE: {mae:.3f}, F1: {f1:.3f}")

    joblib.dump(reg, Path(out_dir) / "cost_reg.joblib")
    joblib.dump(clf, Path(out_dir) / "reliability_clf.joblib")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="./models")
    args = p.parse_args()
    df = load_data(args.data)
    X, yreg, yclf = preprocess(df)
    train(X, yreg, yclf, args.out)


if __name__ == "__main__":
    main()
