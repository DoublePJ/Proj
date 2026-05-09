# Testing Assets

This folder centralizes test artifacts that are shared across backend and frontend.

## Structure

- `api/postman/` — Postman collections for API smoke/manual runs
- `api/robot/` — Robot Framework API suites
- `ui/robot/` — Robot Framework browser UI end-to-end suites
- `backend/` — Backend testing documentation (guide + matrices)
- `frontend/` — Frontend testing documentation (guide + matrices)

## Related Test Locations

- `backend/tests/` — backend automated tests with `pytest`
- `frontend/src/**/*.test.js` — frontend automated tests with Jest + Testing Library

## Backend Testing Docs

- `backend/TESTING.md` — backend test guide
- `backend/TEST_CASES.md` — summary matrix
- `backend/TEST_CASES_APPENDIX.md` — detailed appendix

## Frontend Testing Docs

- `frontend/TESTING.md` — frontend test guide
- `frontend/TEST_CASES.md` — summary matrix
- `frontend/TEST_CASES_APPENDIX.md` — detailed appendix

## Run Hints

From `backend` folder:

```powershell
python -m pytest
python -m robot ../testing/api/robot/conversation_api.robot
python -m robot ../testing/ui/robot/e2e_user_journey_ui.robot
```

From `frontend` folder:

```powershell
npm test -- --watchAll=false --runInBand
```