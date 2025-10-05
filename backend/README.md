# UCRF Backend

FastAPI backend with SQLite database, data pipeline and training scripts.

Quickstart

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

3. Train models:

```powershell
python train.py --data processed.csv --out ./models
```
