# JeevanQR

Emergency QR system for riders and drivers. This repository contains both the frontend static files and the backend FastAPI application used to generate and serve emergency QR codes and associated rescue flows.

Live demo: https://jeevan-qr-5tb1.vercel.app/

## Where to start

- Backend (FastAPI): see `backend/README.md` for setup, quickstart, testing, and deployment instructions.
- Frontend: static files are served from the `frontend/` directory by the backend.

## Quick links

- Run backend locally: `cd backend && uvicorn app.main:app --reload --port 3000`
- Backend docs: open `backend/README.md`

## Contributing & CI

If you'd like CI, I can add a GitHub Actions workflow that runs `ruff` and `pytest` on push and PRs. I can also add a Dockerfile for the backend if you want containerized deployment.

## License

MIT

