# JeevanQR

A lightweight emergency QR system for Indian road users — generate a printable QR containing minimal emergency details so anyone can scan and help without installing an app.

---

Quick links

- Live demo: (deploy to Vercel / your own host)
- Source: This repository

---

**Why JeevanQR**

Road accidents leave victims unable to communicate critical information. JeevanQR lets users create a simple QR code with essential emergency details (name, blood group, emergency contacts, helplines, location sharing). Anyone can scan the QR to call contacts or share location — no app required.

---

## Highlights

- Self-contained QR tokens (serverless-friendly)
- One-tap calls to emergency contacts and government helplines
- Optional location sharing via Google Maps link
- Lightweight frontend (HTML/CSS/JS) + small Node.js backend
- Works on low-bandwidth mobile networks and Android devices

---

## Quick Start

Prerequisites

- Node.js 16+ and npm
- Git

Run locally

1. Clone the repo

```bash
git clone <your-repo-url>
cd JeevanQR
```

2. Install dependencies and start

```bash
npm install
npm start
```

3. Open http://localhost:3000 in a browser.

Notes:

- Use `npm run dev` to start with `nodemon` for quicker local development.

---

## Project Layout

See the main folders:

```
frontend/   # static pages (register, QR, scan, viewers)
backend/    # Express server (API, QR generation, uploads)
database/   # local JSON storage for users, logs, photos (dev only)
uploads/    # saved photos (dev only)
```

Key files

- `frontend/index.html` — registration
- `frontend/scan.html` — rescuer view after scanning QR
- `backend/server.js` — API and QR generation
- `backend/database.js` — simple JSON-based storage for local dev

---

## How it works (short)

1. User registers with name, blood group, emergency contacts and helplines.
2. Backend returns a self-contained token and a QR image URL.
3. QR encodes a link to `/scan/<token>`; rescuer scans and opens the rescue page.
4. Rescue page shows name, blood group, helplines and provides encoded phone links and location sharing.

---

## Deployment

Recommended: Vercel (serverless) or any Node.js host.

1. Push this repository to your GitHub account.
2. Import the repo in Vercel and deploy (Framework: Other).

Environment variables (optional)

- `SITE_URL` — Optional full site URL to use when generating QR image links.

---

## Security & Privacy

- Phone numbers are not displayed as plain text on the rescue page — the frontend uses encoded values and `tel:` links so rescuers can call with one tap.
- Tokens are self-contained and minimal; avoid encoding sensitive personal data.
- For production, enable HTTPS and review any photo upload handling for privacy and retention policies.

---

## Contributing

Improvements welcome — open an issue or a pull request. Suggested steps:

1. Fork the repo
2. Create a branch (`git checkout -b feat/improve-readme`)
3. Commit and push
4. Open a PR with a clear description

---

## License

MIT — see the LICENSE file.

---

If you want, I can now commit this change and push it to a GitHub repository — tell me the target repo URL (for example: `https://github.com/<your-username>/jeevan-qr.git`) or confirm `origin` remote is correct and I will push.
