# QR Emergency Alert System — FastAPI backend

This repository contains the backend API for the JeevanQR emergency QR code system, implemented with Python and FastAPI. It provides user registration, self-contained base64url tokens, QR code generation, accident logging, photo uploads with one-time view links, and lightweight file-based persistence with serverless-friendly fallbacks.

Quick links
- Run locally: `uvicorn app.main:app --reload --port 3000`
- Tests: `python -m pytest -q`
- Lint: `python -m ruff check app`

## Requirements
- Python 3.12+
- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quickstart
1. From the `backend` directory create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies and copy environment file:

```bash
pip install -r requirements.txt
cp .env.example .env
```

3. Start the development server:

```bash
uvicorn app.main:app --reload --port 3000
```

API docs will be available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Environment variables
Configure environment variables in `.env` or your deployment environment. Key variables:

- `PORT` — server port (default `3000`)
- `ALLOWED_ORIGIN` — CORS origin (default `*`)
- `SITE_URL` — base site URL (optional)
- `VERCEL` / `VERCEL_URL` — provided by Vercel when deployed (used to detect serverless)
- `NODE_ENV` — environment mode (e.g., `production`)

## Testing & Linting
- Run tests:

```bash
python -m pytest -q
```

- Run Ruff (lint):

```bash
python -m ruff check app
```

## Project layout

Top-level structure (key files):

```
backend/
├── app/                # FastAPI application package
├── requirements.txt
├── README.md
└── tests and utilities
```

Detailed layout is preserved in the repository; routers are in `app/routers`, services in `app/services`, and Pydantic schemas in `app/schemas`.

## Deployment

The backend supports both traditional server deployment (using `uvicorn`/ASGI) and serverless platforms (Vercel). When deployed to Vercel the app will detect the environment using `VERCEL`/`VERCEL_URL` and adapt storage (in-memory fallback).

## Contribution & CI
- If you want CI, a simple GitHub Actions workflow can run `ruff` and `pytest` on push/PR. I can add a sample workflow on request.

## License
Same as the original project.