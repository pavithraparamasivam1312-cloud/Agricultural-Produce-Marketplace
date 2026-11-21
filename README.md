# HarvestHub — Agricultural Produce Marketplace Operations

A college DevOps project that coordinates farmers, buyers, collection agents and marketplace administrators through an internal produce marketplace.

## Features
- Register and publish produce lots with quantity, category, price and location.
- Browse/search available produce.
- Submit buyer requests against a produce lot.
- Track request negotiation (Pending / Accepted / Rejected).
- Track collection (Not scheduled / Scheduled / Collected).
- Dashboard metrics for listings, requests and collection progress.

## Technology
React + Vite frontend, Python Flask REST API, SQLite database, Docker Compose, GitHub Actions CI.

## Run locally (without Docker)
Terminal 1:
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Terminal 2:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Flask API runs at http://localhost:5000.

## Run with Docker
Install Docker Desktop, then from the project root:
```bash
docker compose up --build
```
Open http://localhost:5173.

## API endpoints
- `GET /api/health`
- `GET /api/produce`, `POST /api/produce`
- `GET /api/requests`, `POST /api/requests`
- `PATCH /api/requests/<id>`

## DevOps workflow
Git version control → GitHub repository → GitHub Actions CI checks → Docker image/container workflow.

## Scope
Internal coordination tool only. It does not process payments or integrate with external logistics services. This starter project is intended for academic demonstration; add authentication, authorization, validation hardening and production database configuration before real-world use.
