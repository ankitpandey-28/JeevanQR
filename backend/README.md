# QR Emergency Alert System - FastAPI Backend

Backend API for the JeevanQR emergency QR code system, built with Python and FastAPI.

## Project Overview

JeevanQR is a critical emergency alert system designed to store vital user information (such as blood group, emergency contacts, and government helplines) securely. This backend provides the necessary infrastructure to handle user registration, self-contained QR code generation via base64url encoded tokens, accident location logging, and photo uploads with secure one-time viewing links. It supports both local file-based storage and serverless deployments with in-memory fallbacks.

## Features

- **User Registration**: Register user details, emergency contacts, and government helplines.
- **Self-contained tokens**: Uses base64url encoded tokens that carry user data, eliminating the need for database lookups on scan.
- **QR code generation**: Dynamic generation of QR code PNG images with embedded scan URLs.
- **Photo uploads**: Support for uploading emergency photos with secure, one-time view links.
- **Accident location logging**: Endpoints to log accident coordinates.
- **Statistics**: Endpoint for monitoring system usage statistics.
- **Static file serving**: Serves HTML, CSS, and JavaScript for the frontend.
- **Serverless compatibility**: Seamless integration with platforms like Vercel.

## Prerequisites

- Python 3.12+
- pip

## Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Copy the environment configuration file:
   ```bash
   cp .env.example .env
   ```

## Environment Variables

The backend uses the following environment variables. Ensure these are set in your `.env` file or deployment environment. Note that `NODE_ENV` is used for environment mode detection (e.g., detecting production or Vercel environments).

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `PORT` | Port for the server to listen on | `3000` |
| `ALLOWED_ORIGIN` | CORS allowed origin | `*` |
| `SITE_URL` | Base URL for the application | `http://localhost:3000` |
| `VERCEL_URL` | Set automatically by Vercel; used if SITE_URL is not set | *(None)* |
| `VERCEL` | Set automatically by Vercel; indicates a serverless environment | `0` or unset |
| `NODE_ENV` | Environment mode detection (e.g., `production`) | `development` |
| `HOME` | Home directory, used to determine storage paths in some environments | *(System default)* |

## Running the Server

Start the application in development mode using uvicorn:

```bash
uvicorn app.main:app --reload --port 3000
```

Alternatively, run it via the Python module:

```bash
python -m uvicorn app.main:app --reload --port 3000
```

The server will be available at `http://localhost:3000`.

## API Documentation

FastAPI provides automatic interactive API documentation. Once the server is running, you can access:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

## API Endpoints

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

## Testing

Run tests using pytest:

```bash
# Run all tests
python -m pytest -v

# Run individual test suites
python -m pytest test_database.py -v
python -m pytest test_api.py -v
python -m pytest test_routes.py -v
```

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   ├── photos.py
│   │   ├── qr.py
│   │   ├── registration.py
│   │   ├── stats.py
│   │   └── users.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── photos.py
│   │   ├── registration.py
│   │   ├── stats.py
│   │   └── users.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── qr_service.py
│   │   ├── token_service.py
│   │   └── validation.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── .env.example
├── requirements.txt
├── test_api.py
├── test_database.py
├── test_routes.py
└── README.md
```

## Deployment

This project is configured for deployment on Vercel as a serverless application.

1. Push the code to a GitHub repository.
2. Import the project into Vercel.
3. Set the following environment variable in your Vercel project settings:
  - `NODE_ENV=production`
4. Vercel automatically provides `VERCEL` and `VERCEL_URL`.

The application automatically detects the Vercel environment and adapts storage mechanisms accordingly.

## License

Same as the original project.