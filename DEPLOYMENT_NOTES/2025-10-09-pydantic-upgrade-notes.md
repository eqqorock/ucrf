Pydantic v2 upgrade notes — 2025-10-09

What I changed
- Updated `backend/requirements.txt` to:
  - `pydantic>=2.0.0,<3.0.0`
  - `fastapi>=0.100.0,<1.0.0`
- Updated `backend/app/main.py`:
  - Replaced `payload.dict()` with `payload.model_dump()` (Pydantic v2 API)

Why
- Pydantic v1 is incompatible with Python 3.13's typing internals. Upgrading to pydantic v2 avoids the ForwardRef._evaluate error on newer Python versions.

Notes & next steps
- I scanned the `backend/` directory for common Pydantic v1 patterns (validators, Config classes, `.json()` calls) and found none beyond the replaced `.dict()` call. This means the upgrade is likely low-risk for this codebase.
- Deploy tip: if you still want to pin runtime to Python 3.11, do so on Render; otherwise the app should work on newer Python after this upgrade.
- Monitor the deploy logs for any additional migration warnings from Pydantic or FastAPI.

If you want, I can:
- Add a small automated smoke test that imports the app and exercises the endpoints in CI.
- Prepare a PR with tests and a GitHub Actions workflow to run the app import under Python 3.13 to verify compatibility automatically.
