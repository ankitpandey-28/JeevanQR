# JeevanQR - Emergency QR Code System

> A life-saving QR code system for Indian road users. Generate a QR code with your emergency information that anyone can scan during an accident to quickly contact your family and emergency services.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Demo](#demo)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Security & Privacy](#security--privacy)
- [Good Samaritan Law](#good-samaritan-law-india)
- [License](#license)

---

## About

**JeevanQR** (जीवन QR) is a web-based emergency alert system designed specifically for Indian road users. The name "Jeevan" means "Life" in Hindi.

### Problem Statement
- Road accidents in India kill over 150,000 people annually
- Victims often can't communicate their identity or contact information
- Bystanders hesitate to help due to lack of information

### Solution
- Users create a QR code with their emergency details
- QR code can be placed on helmets, bikes, or cars
- Anyone can scan it during emergencies to get help quickly
- No app installation required - works on any smartphone

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Step Registration** | Name, blood group, emergency contacts & government helplines |
| **QR Code Generation** | Downloadable/printable QR for helmet, bike, or car |
| **No Login Required** | Rescuers can scan and help without authentication |
| **Privacy-First** | Emergency contact numbers hidden from web page |
| **Indian Helplines** | One-tap call to 112, 108, 101, 102, 1091 |
| **Location Sharing** | Capture GPS and share via SMS/WhatsApp |
| **Emergency Camera** | Capture accident scene photos |
| **Bilingual UI** | English + Hindi for Indian users |
| **Mobile-First** | Optimized for Android, works on 2G/3G |
| **Serverless Ready** | Works on Vercel with self-contained tokens |

---

## Demo

### User Flow

1. **Register** - Enter your name, blood group, emergency contacts
2. **Add Helplines** - Select government helplines (112, 108, etc.)
3. **Generate QR** - Download and print your emergency QR code
4. **Attach QR** - Place on helmet, bike, or car dashboard
5. **Emergency** - If accident occurs, anyone can scan and help

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Node.js + Express.js |
| **Database** | JSON file storage (local) / Self-contained tokens (serverless) |
| **QR Generation** | `qrcode` npm package |
| **Deployment** | Vercel (recommended) |
| **Maps** | Google Maps links (no API key needed) |

---

## Project Structure

```
JeevanQR/
├── frontend/                    # Client-side files
│   ├── index.html              # Registration page
│   ├── emergency-contacts.html # Emergency contacts form
│   ├── government-helplines.html # Helplines selection
│   ├── privacy-settings.html   # Privacy options
│   ├── qr.html                 # QR display/download page
│   ├── scan.html               # Emergency page (for rescuers)
│   ├── photo-view.html         # Emergency photo viewer
│   ├── css/
│   │   └── styles.css          # Red/white emergency theme
│   └── js/
│       ├── config.js           # API configuration
│       ├── register.js         # Registration logic
│       ├── emergency-contacts.js # Contacts management
│       ├── government-helplines.js # Helplines & QR generation
│       ├── qr.js               # QR display logic
│       ├── scan.js             # Emergency page logic
│       ├── location-sharing.js # GPS & sharing service
│       └── emergency-camera.js # Camera capture service
│
├── backend/                     # Server-side files
│   ├── server.js               # Express.js server
│   └── database.js             # Database operations
│
├── database/                    # Local data storage
│   ├── users.json              # User records
│   └── accident_logs.json      # Accident location logs
│
├── package.json                # Dependencies & scripts
├── vercel.json                 # Vercel deployment config
├── .gitignore                  # Git ignore rules
└── README.md                   # Documentation
```

---

## Installation

### Prerequisites

- Node.js v16 or higher - [Download](https://nodejs.org)
- Git - [Download](https://git-scm.com)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/ankitpandey-28/JeevanQR.git

# 2. Navigate to project directory
cd JeevanQR

# 3. Install dependencies
npm install

# 4. Start development server
npm start

# 5. Open in browser
# http://localhost:3000
```

---

## Deployment

### Vercel (Recommended)

1. **Push to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Framework Preset: **Other**
   - Click **Deploy**

3. **Done!** Your app will be live at `https://your-project.vercel.app`

### Environment Variables (Optional)

| Variable | Description |
|----------|-------------|
| `SITE_URL` | Custom domain URL (e.g., `https://jeevanqr.com`) |

---

## API Reference

### Frontend Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Registration page |
| GET | `/emergency-contacts.html` | Emergency contacts form |
| GET | `/government-helplines.html` | Helplines selection |
| GET | `/qr.html?token=xxx` | QR display page |
| GET | `/scan/:token` | Emergency page (rescuer view) |

### Backend APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register user, returns token & QR URL |
| GET | `/api/qr/:token` | Get QR code image (PNG) |
| GET | `/api/users/:token/public` | Get public user info |
| POST | `/api/users/:token/location` | Log accident location |
| POST | `/api/upload-photo` | Upload emergency photo |
| GET | `/api/stats` | Get database statistics |

### Request/Response Examples

**Register User**
```bash
POST /api/register
Content-Type: application/json

{
  "fullName": "Rajesh Kumar",
  "bloodGroup": "O+",
  "emergencyContacts": [
    { "name": "Wife", "phone": "9876543210" }
  ],
  "governmentHelplines": [
    { "name": "Emergency", "number": "112" }
  ]
}
```

**Response**
```json
{
  "token": "eyJuIjoiUmFqZXNoIEt1bWFyIi...",
  "publicUrl": "/scan/eyJuIjoiUmFqZXNoIEt1bWFyIi...",
  "qrImageUrl": "/api/qr/eyJuIjoiUmFqZXNoIEt1bWFyIi..."
}
```

---

## How It Works

### Registration Flow
```
User fills form → Emergency Contacts → Government Helplines
                                              ↓
                                     POST /api/register
                                              ↓
                                     Generate self-contained token
                                              ↓
                                     Return QR code URL
```

### Emergency Scan Flow
```
Rescuer scans QR → Opens full URL (https://site.com/scan/token)
                                              ↓
                              Token contains all user data
                                              ↓
                              Display name, blood group, contacts
                                              ↓
                              One-tap call to emergency contacts
```

### Location Sharing Flow
```
Rescuer clicks "Share Location" → Get GPS coordinates
                                              ↓
                                     Generate Google Maps link
                                              ↓
                              Share via SMS/WhatsApp to all contacts
```

---

## Security & Privacy

| Aspect | Implementation |
|--------|----------------|
| **Hidden Phone Numbers** | Never displayed on page, only used in `tel:` links |
| **Self-Contained Tokens** | User data encoded in token, no database lookup needed |
| **No Authentication** | Privacy by design - minimal data collection |
| **Read-Only Scan Page** | Rescuers cannot modify any data |
| **Base64 Encoding** | Phone numbers encoded before sending to client |
| **HTTPS Only** | All traffic encrypted in production |

---

## Good Samaritan Law (India)

The system displays this message to rescuers:

> **English:** "You are legally protected while helping."
>
> **Hindi:** "आप मदद कर रहे हैं, कानून के अनुसार आप सुरक्षित हैं।"

This complies with Supreme Court of India's 2016 guidelines that protect Good Samaritans from legal harassment.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Inspired by the need for better road safety in India
- Thanks to all contributors and testers
- Dedicated to saving lives on Indian roads

---

**Made with love for India**
