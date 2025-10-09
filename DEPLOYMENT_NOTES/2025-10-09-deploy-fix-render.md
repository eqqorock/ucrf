Render deployment failure diagnosis — 2025-10-09

Summary
-------
Problem: Render deployment failed during startup. The error occurred while importing FastAPI/pydantic models:

TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'

Root cause: Render ran Python 3.13.4 while the project pins `pydantic==1.10.12` and `fastapi==0.95.2` in `backend/requirements.txt`. Pydantic v1 is incompatible with CPython 3.13 typing internals, causing the startup import error.

Decision
--------
Immediate fix chosen: Option A — Force the Render service runtime to Python 3.11.x (compatible with pinned dependencies). This is the least invasive fix and gets the service running quickly.

Actions to apply on Render
--------------------------
1. Open the Render dashboard and select the specific service for this repository.
2. Click the "Settings" tab for the service.
3. Under "Environment" or "Runtime", find the "Python Version" dropdown or runtime setting.
4. Select "3.11.12" (or any 3.11.x available).
5. Save the changes and trigger a redeploy (there's usually a "Manual Deploy" or "Redeploy" button).

Notes
-----
- The repo already contains `runtime.txt` with `python-3.11.12`. Render may have been configured to use a different runtime in the dashboard, which overrides `runtime.txt` for the active service.
- After deployment is successful, consider planning an upgrade to Pydantic v2 and updated FastAPI later (on a dedicated branch), which would allow using newer Python versions.

Chat transcript (selected parts)
--------------------------------
- User reported Render logs showing Python 3.13.4 and a TypeError from pydantic/typing.
- I diagnosed a compatibility issue between Python 3.13 and pydantic v1.
- User chose Option A: set Render Python to 3.11 and asked to save this chat to GitHub.

Saved by: automated assistant
Date: 2025-10-09
