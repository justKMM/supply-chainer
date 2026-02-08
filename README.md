# Supply Chainer
Tomorrow’s agentic logistics network

## Overview
Supply Chainer is a FastAPI backend + React frontend demo that simulates an AI‑native supply chain network. It includes:
- A procurement cascade that discovers suppliers, negotiates, checks compliance, and builds a final execution plan.
- Live agent messaging via SSE.
- Trust/reputation scoring that evolves with each cascade.
- Policy evaluation, risk propagation, and event simulation.
- Product catalogue + profit reporting.

Public URL (Cloud Run):
- https://supply-chainer-379894741496.europe-west1.run.app

## Repository Structure
- `backend/` — FastAPI app, services, agents, schemas
- `frontend/` — React (Vite) UI
- `run.py` — dev runner for backend (and optional UI notes)

## Requirements
- Python 3.11+ (3.12 OK)
- Node.js 20+ (for Vite)
- Docker (optional, for containerized deploy)

## Environment Variables
Create a `.env` in the repo root or set env vars in your shell:

Required for AI features:
- `OPENAI_API_KEY` — OpenAI API key

Optional:
- `SERVE_FRONTEND=true` — serve built frontend from backend (for Docker/Cloud Run)
- `VITE_API_BASE_URL` — frontend API base (only needed if decoupled)
- `AGENT_PROTOCOL_SECRET` — HMAC signing for agent protocol (optional)
- `ENABLE_EXTERNAL_AGENT_TRANSPORT=true` — send protocol messages over HTTP (optional)

## Local Development (Backend + Frontend)

### 1) Backend (FastAPI)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r backend/requirements.txt
python run.py
```

Backend will run at `http://localhost:8000`.

### 2) Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:5173`.

If you want the frontend to call a different backend:
```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Docker (Single Container)

Build and run:
```bash
docker build -t supply-chainer .
docker run --rm -e PORT=8080 -e SERVE_FRONTEND=true -e OPENAI_API_KEY=YOUR_KEY -p 8080:8080 supply-chainer
```

Open:
- `http://localhost:8080/` (frontend)
- `http://localhost:8080/docs` (API)

## Cloud Run (Single Container)

Enable APIs:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

Build & push:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/supply-chainer
```

Deploy:
```bash
gcloud run deploy supply-chainer \
  --image gcr.io/PROJECT_ID/supply-chainer \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars SERVE_FRONTEND=true,OPENAI_API_KEY=YOUR_KEY
```

## Key API Endpoints
- `POST /registry/trigger` — start a cascade
- `GET /api/progress` — cascade progress
- `GET /api/report` — latest report
- `GET /api/stream` — SSE live messages
- `GET /api/catalogue` — product catalogue
- `GET /api/suppliers` — suppliers list
- `GET /api/cascades` — past cascade summaries
- `GET /api/cascades/{report_id}` — report by id

## Notes
- The frontend can run decoupled or served from the backend (Docker/Cloud Run).
- `0.0.0.0` is a bind address — use `http://localhost:PORT` in your browser.
