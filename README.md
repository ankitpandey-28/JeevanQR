# QR-based Emergency Alert System for Road Accidents (India)

A lightweight, web-based emergency alert system designed for Indian road users. Users can generate a QR code containing their emergency information, which can be scanned by anyone during an accident to quickly contact family members and emergency services.

---

## Project Structure

```
QR-based Emergency Alert System/
│
├── frontend/                    # FRONTEND (Client-side)
│   ├── index.html              # Registration page
│   ├── qr.html                 # QR display/download page
│   ├── scan.html               # Emergency page (for rescuers)
│   ├── css/
│   │   └── styles.css          # Red/white emergency theme
│   └── js/
│       ├── register.js         # Registration form logic
│       ├── qr.js               # QR display logic
│       └── scan.js             # Emergency page logic
│
├── backend/                     # BACKEND (Server-side)
│   ├── server.js               # Express.js server (routes + APIs)
│   └── database.js             # Database module (CRUD operations)
│
├── database/                    # DATABASE (Data storage)
│   ├── users.json              # User records (token -> user data)
│   └── accident_logs.json      # Accident location logs
│
├── package.json                # Node.js dependencies & scripts
├── Procfile                    # Heroku/Render deployment
├── vercel.json                 # Vercel deployment config
├── render.yaml                 # Render.com deployment config
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## Features

| Feature | Description |
|---------|-------------|
| Simple Registration | Enter name, blood group, and emergency contact |
| QR Code Generation | Downloadable/printable QR for helmet, bike, or car |
| No Login Required | Rescuers can scan and help without authentication |
| Privacy-First | Emergency contact number hidden from web page |
| Indian Helplines | One-tap call to 112 (Emergency) and 108 (Ambulance) |
| Location Sharing | Capture GPS and share via SMS/WhatsApp |
| Bilingual UI | English + Hindi for Indian users |
| Mobile-First | Optimized for Android, works on 2G/3G |
| Good Samaritan Compliant | Legal protection message for rescuers |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Node.js with Express.js |
| **Database** | JSON file storage |
| **QR Generation** | `qrcode` npm package |
| **Maps** | Google Maps links (no API key needed) |

---

## Installation & Running

### Prerequisites
- Node.js v16 or higher ([Download](https://nodejs.org))

### Steps

1. **Open terminal** in project folder:
   ```bash
   cd "QR-based Emergency Alert System for Road Accidents"
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the server**:
   ```bash
   npm start
   ```

4. **Open in browser**:
   ```
   http://localhost:3000
   ```

---

## API Endpoints

### Frontend Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Registration page |
| GET | `/qr.html` | QR display page |
| GET | `/scan/:token` | Emergency page (rescuer view) |

### Backend APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register user, returns token |
| GET | `/api/qr/:token` | Get QR code image (PNG) |
| GET | `/api/users/:token/public` | Get public user info |
| POST | `/api/users/:token/location` | Log accident location |
| GET | `/api/stats` | Get database statistics |

---

## Data Flow

### 1. Registration Flow
```
User → index.html → POST /api/register → backend/server.js
                                              ↓
                                     backend/database.js
                                              ↓
                                     database/users.json
                                              ↓
                                     Return token + QR URL
```

### 2. QR Scan Flow
```
Rescuer scans QR → Opens /scan/:token → scan.html
                                              ↓
                                     GET /api/users/:token/public
                                              ↓
                                     backend/database.js → users.json
                                              ↓
                                     Display name + blood group
```

### 3. Location Share Flow
```
Rescuer clicks "Share Location" → Browser Geolocation API
                                              ↓
                                     POST /api/users/:token/location
                                              ↓
                                     database/accident_logs.json
                                              ↓
                                     Share via SMS/WhatsApp
```

---

## Database Schema

### users.json
```json
{
  "a1b2c3d4e5f6...": {
    "fullName": "Rajesh Kumar",
    "bloodGroup": "O+",
    "emergencyContact": "9876543210",
    "createdAt": "2026-01-29T10:30:00.000Z"
  }
}
```

### accident_logs.json
```json
[
  {
    "id": 1706520600000,
    "token": "a1b2c3d4e5f6...",
    "userName": "Rajesh Kumar",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "mapsUrl": "https://www.google.com/maps?q=28.6139,77.2090",
    "reportedAt": "2026-01-29T10:30:00.000Z"
  }
]
```

---

## Deployment

### Option 1: Render.com (Recommended - Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Settings:
   - Build Command: `npm install`
   - Start Command: `node backend/server.js`
5. Deploy → Get public URL

### Option 2: Railway.app

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Auto-detects Node.js
4. Get public URL

### Option 3: Vercel

```bash
npm i -g vercel
vercel
```

### Option 4: Local Network Demo

```bash
# Find your IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# Start server
npm start

# Access from phone (same WiFi)
http://YOUR_IP:3000
```

---

## Security & Privacy

| Aspect | Implementation |
|--------|----------------|
| Hidden Phone Number | Never displayed on scan page, only used in `tel:` link |
| Token-Based Access | Random 32-char hex tokens prevent guessing |
| No Authentication | Privacy by design - minimal data collection |
| Read-Only Scan Page | Rescuers cannot modify any data |
| Base64 Encoding | Phone number encoded before sending to client |

---

## Good Samaritan Law (India)

The system displays this message to rescuers:

> **English:** "You are legally protected while helping."
>
> **Hindi:** "आप मदद कर रहे हैं, कानून के अनुसार आप सुरक्षित हैं।"

This complies with Supreme Court of India's 2016 guidelines.

---

## For Exam/Viva

### Key Points

1. **Why web-based?** Works on any phone without app installation
2. **Why no login for rescuer?** Emergency needs instant access
3. **How is privacy maintained?** Phone number hidden, only `tel:` link used
4. **Why JSON storage?** Lightweight, no DB setup, easy to understand
5. **Why separate folders?** Clean architecture (frontend/backend/database)

### Demo Steps

1. Start server: `npm start`
2. Open `localhost:3000` on laptop
3. Register with sample data
4. Show QR generation
5. Scan QR with phone → Emergency page opens
6. Demo call buttons and location sharing
7. Show `database/users.json` to explain storage

---

## License

MIT License - Free for educational and personal use.
#   J e e v a n Q R  
 