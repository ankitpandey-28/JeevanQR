# QR Emergency Alert System - Python/FastAPI Backend

A complete Python/FastAPI migration of the original Node.js/Express backend for the JeevanQR emergency QR code system.

## Overview

This backend provides:
- **User Registration** with emergency contacts and government helplines
- **Self-contained tokens** (base64url encoded) that carry all user data — no database lookup needed
- **QR code generation** (PNG images)
- **Photo uploads** with one-time secure view links
- **Accident location logging**
- **Statistics** endpoint
- **Static file serving** for the frontend (HTML, CSS, JS)
- **Serverless compatibility** (Vercel-ready)

## Architecture

```
backend/
├── app/
│   ├── __init__.py           # Package init
│   ├── config.py             # Pydantic Settings (Module 1)
│   ├── database.py           # JSON file storage (Module 1)
│   ├── main.py               # FastAPI app entry point (Module 3)
│   ├── middleware/
│   │   ├── __init__.py       # Package init (Module 2)
│   │   └── error_handler.py  # HTTP 404/500 handlers (Module 2)
│   ├── routers/
│   │   ├── __init__.py       # Package init (Module 3)
│   │   ├── pages.py          # Static HTML page routes (Module 3)
│   │   ├── photos.py         # Photo upload/view routes (Module 3)
│   │   ├── qr.py             # QR generation route (Module 3)
│   │   ├── registration.py   # User registration route (Module 3)
│   │   ├── stats.py          # Statistics route (Module 3)
│   │   └── users.py          # User public data / location routes (Module 3)
│   ├── schemas/
│   │   ├── __init__.py       # Package init (Module 2)
│   │   ├── photos.py         # Photo upload schemas (Module 2)
│   │   ├── registration.py   # Registration request/response schemas (Module 2)
│   │   ├── stats.py          # Statistics response schema (Module 2)
│   │   └── users.py          # User data / location schemas (Module 2)
│   ├── services/
│   │   ├── __init__.py       # Package init (Module 1)
│   │   ├── qr_service.py     # QR code generation (Module 1)
│   │   ├── token_service.py  # Token encode/decode (Module 1)
│   │   └── validation.py     # Phone validation utilities (Module 1)
│   └── utils/
│       ├── __init__.py       # Package init (Module 1)
│       └── helpers.py        # Token generation, base64 encoding (Module 1)
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
├── test_module1.py           # Module 1 unit tests
├── test_module2.py           # Module 2 unit tests
├── test_database.py          # Database pytest suite
├── test_api.py               # API endpoint pytest suite
├── test_routes.py            # Route-level pytest suite
└── README.md                 # This file
```

## Prerequisites

- Python 3.12+
- pip

## Installation

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

## Running the Server

```bash
# Start with uvicorn (development)
uvicorn app.main:app --reload --port 3000

# Or with the provided startup script
python -m uvicorn app.main:app --reload --port 3000
```

The server will be available at `http://localhost:3000`.

## API Endpoints

All endpoints match the original Node.js backend exactly:

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | Home page (index.html) |
| `GET` | `/scan/{token}` | Emergency scan page |
| `GET` | `/qr.html` | QR display page |
| `GET` | `/emergency-contacts.html` | Emergency contacts page |
| `GET` | `/government-helplines.html` | Government helplines page |
| `GET` | `/privacy-settings.html` | Privacy settings page |
| `GET` | `/photo/{viewToken}` | One-time photo view page |
| `POST` | `/api/register` | Register a new user |
| `GET` | `/api/qr/{token}` | Generate QR code PNG |
| `GET` | `/api/users/{token}/public` | Get public user info |
| `POST` | `/api/users/{token}/location` | Log accident location |
| `GET` | `/api/stats` | Get statistics |
| `POST` | `/api/upload-photo` | Upload emergency photo |

### Registration

```json
POST /api/register
{
  "fullName": "Ravi Kumar",
  "bloodGroup": "B+",
  "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
  "governmentHelplines": [{"name": "Police", "number": "100"}]
}

Response 200:
{
  "token": "<base64url-encoded-token>",
  "publicUrl": "/scan/<token>",
  "qrImageUrl": "/api/qr/<token>"
}
```

### QR Code

```http
GET /api/qr/{token}
Response: image/png (QR code with scan URL embedded)
Cache-Control: public, max-age=31536000
```

### Public User Info

```json
GET /api/users/{token}/public

Response 200:
{
  "fullName": "Ravi Kumar",
  "bloodGroup": "B+",
  "emergencyContacts": [{"name": "Sunita", "phoneEncoded": "<base64>"}],
  "governmentHelplines": [{"name": "Police", "number": "100"}]
}
```

### Accident Location

```json
POST /api/users/{token}/location
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090"
}

Response 200:
{ "ok": true }
```

### Photo Upload

```http
POST /api/upload-photo
Content-Type: multipart/form-data

Fields:
- photo: file (image)
- token: string
- patientName: string (optional)
- timestamp: string (optional)

Response 200:
{
  "success": true,
  "photoUrl": "/uploads/emergency-<id>.jpg",
  "secureUrl": "http://host/photo/<viewToken>",
  "viewToken": "<hex>",
  "message": "Photo uploaded successfully"
}
```

### Statistics

```json
GET /api/stats

Response 200:
{
  "totalUsers": 0,
  "totalAccidentLogs": 0,
  "totalPhotos": 0,
  "lastUpdated": "2024-01-01T00:00:00.000Z"
}
```

## Running Tests

```bash
# Module verification scripts
python test_module1.py
python test_module2.py

# Pytest suites
python -m pytest test_database.py -v
python -m pytest test_api.py -v
python -m pytest test_routes.py -v

# Run all tests
python -m pytest -v
```

## Deployment (Vercel)

This project is ready for deployment on Vercel as a serverless function.

1. Push to a GitHub repository.
2. Import into Vercel.
3. Set the following environment variables in Vercel:
   - `NODE_ENV=production`
4. Vercel automatically sets `VERCEL` and `VERCEL_URL`.

No additional configuration is needed. The app detects serverless environments and switches to in-memory storage automatically.

For the `vercel.json` configuration, see the project root.

## Migration Notes

This backend is a direct migration of the original Node.js/Express backend (`legacy-backend/server.js`). Key differences:

| Aspect | Node.js | Python/FastAPI |
|--------|---------|----------------|
| Framework | Express | FastAPI |
| Language | JavaScript | Python 3.12+ |
| Validation | Manual | Pydantic v2 |
| Typing | JSDoc | Type hints |
| Async | Async/await | Async/await |
| Settings | process.env | pydantic-settings |
| QR Code | qrcode npm | qrcode[pil] PyPI |
| Storage | JSON files | JSON files (same format) |

All business logic, data formats, and API contracts remain identical.

## Original Node.js Backend

The original Express.js backend is located at `legacy-backend/server.js` in the project root for reference during the migration.

## License

Same as the original project.