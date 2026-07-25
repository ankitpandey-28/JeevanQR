# JeevanQR

Emergency QR system for Indian road users — generate a printable QR code with critical accident details so anyone can scan and help immediately.

Live demo: https://jeevan-qr-5tb1.vercel.app/

---

## Overview

JeevanQR helps riders and drivers carry an emergency-ready QR code for road accidents. The user creates a compact QR containing only the most important information: name, blood group, emergency contacts, and helplines.

Anyone can scan the QR without installing an app. The scan page shows call-ready emergency contacts, government helplines, and supports accident location sharing and one-time photo upload.

---

## Key Features

- **Emergency QR creation** with name and blood group
- **Multiple emergency contacts** with one-tap calling
- **Government helplines** for police, ambulance, and rescue services
- **Downloadable QR image** for helmets, bikes, cars, or ID cards
- **Scan page for rescuers** with clear emergency details
- **Auto location sharing** via WhatsApp or SMS fallback
- **Accident photo capture** and one-time secure sharing
- **Privacy settings** for contact visibility and data retention
- **Good Samaritan guidance** in English and Hindi
- **Serverless-compatible backend** with self-contained tokens
- **Lightweight frontend** using HTML, CSS, and JavaScript

---

## How It Works

1. Open the app and enter your full name and blood group.
2. Add one or more emergency contacts.
3. Add government helplines and optionally configure privacy settings.
4. Generate and download the emergency QR code.
5. A rescuer scans the QR and opens a mobile-friendly emergency page.
6. The rescuer can call emergency contacts, call helplines, share location, or send an accident photo.

---

## Pages Included

- `frontend/index.html` — Register user details and start QR creation
- `frontend/emergency-contacts.html` — Add emergency contact names and phone numbers
- `frontend/government-helplines.html` — Add important official helpline numbers
- `frontend/privacy-settings.html` — Configure privacy and data retention options
- `frontend/qr.html` — View and download the generated QR image
- `frontend/scan.html` — Emergency rescue page shown after scanning the QR

---

## Backend & API

The backend runs on **Python + FastAPI** and serves the frontend plus API routes:

- `POST /api/register` — create a user token and registration data
- `GET /api/qr/{token}` — generate QR code PNG for the emergency page URL
- `GET /api/users/{token}/public` — return public patient and contact details
- `POST /api/users/{token}/location` — log accident location data
- `GET /api/stats` — return basic usage statistics
- `POST /api/upload-photo` — upload an accident photo with one-time view sharing

Tokens are self-contained base64url strings that encode the emergency data, allowing the scan page to display patient info without requiring a persistent session lookup.

---

## Tech Stack

- Frontend: `HTML`, `CSS`, `JavaScript`
- Backend: `Python`, `FastAPI`, `Uvicorn`
- QR generation: `qrcode[pil]`
- Static assets: served from `frontend/`
- Local storage: `database/` JSON files for development

---

## Installation

### Prerequisites

- Python 3.12+
- `pip`
- Optional: `git`

### Run locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

Then open:

```text
http://localhost:3000
```

### Development notes

- The backend serves static frontend files from `frontend/`
- Uploaded photos are saved in `uploads/`
- The repository includes local JSON storage in `database/` for quick testing

---

## Project Structure

```text
backend/               # Python/FastAPI backend
  app/
    config.py          # environment and path settings
    main.py            # FastAPI app and route mounting
    routers/           # API and page routes
    schemas/           # request/response validation models
    services/          # token, QR, and validation helpers
    utils/             # support utilities
frontend/              # static app pages and JS
database/              # local JSON storage files (dev only)
uploads/               # saved uploaded photos
```

---

## Deployment

This project is optimized for serverless deployment such as Vercel. To deploy:

1. Push the repository to GitHub.
2. Import the repo in Vercel.
3. Configure `python -m uvicorn backend.app.main:app` or use the `backend` folder setup.

> Live demo: https://jeevan-qr-5tb1.vercel.app/

---

## Privacy & Safety

- Emergency phone numbers are not shown directly on the public scan page.
- The QR token only contains the minimum needed emergency data.
- The scan page is mobile-first and built for fast rescuer access.
- Good Samaritan guidance is displayed to encourage safe help.

---

## Contributing

Feel free to contribute improvements, bug fixes, and new features.

1. Fork the repo
2. Create a branch
3. Open a pull request

---

## License

MIT

