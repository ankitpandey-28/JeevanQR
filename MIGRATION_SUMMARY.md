# Migration Summary

## Backend swap completed

The old Node.js backend was preserved under the backup folder and the FastAPI backend is now the active backend for the project.

## Files moved / preserved

### Moved to backup
- legacy-backend/server.js
- legacy-backend/database.js

### Active backend now used
- backend/app/main.py
- backend/app/database.py
- backend/app/routers/*
- backend/app/services/*
- backend/app/schemas/*

## Files renamed
- backend-python -> backend

## Configuration changes
- package.json now starts the FastAPI server with uvicorn.
- vercel.json now targets the FastAPI entrypoint.
- README.md now documents the Python/FastAPI workflow.
- frontend favicon instructions were updated to match the FastAPI backend.

## Final project structure

```text
JeevanQR/
├── backend/            # Active FastAPI backend
├── legacy-backend/     # Backup of the original Node.js backend
├── database/           # JSON persistence files
├── frontend/           # Static web app
├── uploads/            # Uploaded photos
├── package.json
├── README.md
├── vercel.json
```

## Verification

### Tests
- Ran: python -m pytest -v
- Result: 79 passed

### Live server check
- Started FastAPI server on http://127.0.0.1:3000
- Verified routes: /, /api/stats, /qr.html, /scan/test-token
