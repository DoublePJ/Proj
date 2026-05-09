# React Frontend

## Overview
This is the frontend of the Thai Labour Law Chatbot, built with React (Create React App). It communicates with the FastAPI backend and provides the chat UI and library pages.

## Folder structure (short)
- `public/` — static HTML and manifest
- `src/` — app source
  - `components/` — UI components
  - `pages/` — page-level components
  - `services/` — API client utilities
  - `contexts/` — React contexts for auth and library
  - `styles/` — global CSS

## Local development
1. Install dependencies and start dev server:

```bash
cd frontend
npm install
npm start
```

2. Open http://localhost:3000 in your browser. The frontend expects the backend API to be running (default: http://127.0.0.1:8000).

## Build for production

```bash
cd frontend
npm run build
```

The production-ready files will be in the `build/` folder.

## Notes
- If the frontend cannot reach the backend, confirm the backend is running and CORS settings allow the origin. See `backend/main.py` for CORS config.
- For environment-specific variables, check `package.json` scripts or create a `.env` file following CRA conventions (e.g., `REACT_APP_BASE_API_URL=http://127.0.0.1:8000`). Use [frontend/.env.example](.env.example) as the template.

## See also
- Root README: [README.md](../README.md)
- Backend README: [backend/README.md](../backend/README.md)
- Frontend testing guide: [testing/frontend/TESTING.md](../testing/frontend/TESTING.md)
