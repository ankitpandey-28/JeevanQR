/**
 * QR Emergency Alert System - Backend Server
 * Express.js server handling registration, QR generation, and emergency data
 */

const express = require('express');
const path = require('path');
const crypto = require('crypto');
const bodyParser = require('body-parser');
const QRCode = require('qrcode');

// Import database module
const db = require('./database');

// ============================================
// EXPRESS APP SETUP
// ============================================

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// ============================================
// STATIC FILE SERVING (Frontend)
// ============================================

const FRONTEND_DIR = path.join(__dirname, '..', 'frontend');

// Serve static assets (CSS, JS)
app.use('/css', express.static(path.join(FRONTEND_DIR, 'css')));
app.use('/js', express.static(path.join(FRONTEND_DIR, 'js')));

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Generate secure random token
 * @returns {string} 32-character hex token
 */
function generateToken() {
  return crypto.randomBytes(16).toString('hex');
}

/**
 * Validate Indian phone number format
 * @param {string} phone - Phone number to validate
 * @returns {boolean}
 */
function isValidIndianPhone(phone) {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length >= 10 && cleaned.length <= 13;
}

/**
 * Clean phone number to digits only
 * @param {string} phone - Phone number
 * @returns {string}
 */
function cleanPhoneNumber(phone) {
  return phone.replace(/\D/g, '');
}

/**
 * Encode string to base64
 * @param {string} str - String to encode
 * @returns {string}
 */
function encodeBase64(str) {
  return Buffer.from(str, 'utf8').toString('base64');
}

// ============================================
// HTML PAGE ROUTES
// ============================================

// Home/Registration page
app.get('/', (req, res) => {
  res.sendFile(path.join(FRONTEND_DIR, 'index.html'));
});

// QR display page
app.get('/qr.html', (req, res) => {
  res.sendFile(path.join(FRONTEND_DIR, 'qr.html'));
});

// Emergency scan page (for rescuers)
app.get('/scan/:token', (req, res) => {
  res.sendFile(path.join(FRONTEND_DIR, 'scan.html'));
});

// ============================================
// API ROUTES
// ============================================

/**
 * POST /api/register
 * Register a new user and generate token
 */
app.post('/api/register', (req, res) => {
  const { fullName, bloodGroup, emergencyContact } = req.body;

  // Validate required fields
  if (!fullName || !bloodGroup || !emergencyContact) {
    return res.status(400).json({ 
      error: 'Missing required fields. सभी जानकारी आवश्यक है।' 
    });
  }

  // Validate phone number format
  if (!isValidIndianPhone(emergencyContact)) {
    return res.status(400).json({ 
      error: 'Invalid emergency contact number. अमान्य फोन नंबर।' 
    });
  }

  // Generate unique token
  const token = generateToken();

  // Create user record
  const user = {
    fullName: fullName.trim(),
    bloodGroup: bloodGroup.trim().toUpperCase(),
    emergencyContact: cleanPhoneNumber(emergencyContact),
    createdAt: new Date().toISOString()
  };

  // Save to database
  db.saveUser(token, user);

  // Build response URLs
  const publicUrl = `${req.protocol}://${req.get('host')}/scan/${token}`;

  res.json({
    token,
    publicUrl,
    qrImageUrl: `/api/qr/${token}`
  });
});

/**
 * GET /api/qr/:token
 * Generate and return QR code image (PNG)
 */
app.get('/api/qr/:token', async (req, res) => {
  const { token } = req.params;
  
  // Check if user exists
  const user = db.getUser(token);
  if (!user) {
    return res.status(404).send('Unknown QR code');
  }

  // Build URL to encode in QR
  const publicUrl = `${req.protocol}://${req.get('host')}/scan/${token}`;

  try {
    res.setHeader('Content-Type', 'image/png');
    res.setHeader('Cache-Control', 'public, max-age=31536000'); // Cache for 1 year
    
    await QRCode.toFileStream(res, publicUrl, {
      errorCorrectionLevel: 'M',
      margin: 1,
      width: 512
    });
  } catch (err) {
    console.error('QR generation failed:', err);
    res.status(500).send('Failed to generate QR code');
  }
});

/**
 * GET /api/users/:token/public
 * Get public user info (no raw phone number)
 */
app.get('/api/users/:token/public', (req, res) => {
  const { token } = req.params;
  
  const user = db.getUser(token);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  // Return public data only
  // Phone number is base64-encoded (not shown as text on page)
  res.json({
    fullName: user.fullName,
    bloodGroup: user.bloodGroup,
    contactEncoded: encodeBase64(user.emergencyContact)
  });
});

/**
 * POST /api/users/:token/location
 * Log accident location (for monitoring/future features)
 */
app.post('/api/users/:token/location', (req, res) => {
  const { token } = req.params;
  
  const user = db.getUser(token);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  const { latitude, longitude, mapsUrl } = req.body || {};

  // Log the accident location
  db.logAccidentLocation(token, {
    userName: user.fullName,
    latitude,
    longitude,
    mapsUrl,
    reportedAt: new Date().toISOString()
  });

  res.json({ ok: true });
});

/**
 * GET /api/stats
 * Get basic statistics (for admin/demo)
 */
app.get('/api/stats', (req, res) => {
  const stats = db.getStats();
  res.json(stats);
});

// ============================================
// STATIC FILE SERVING (Favicons)
// ============================================

// Serve favicon files from frontend directory
app.use(express.static(FRONTEND_DIR));

// ============================================
// ERROR HANDLING
// ============================================

// 404 handler
app.use((req, res) => {
  res.status(404).send('Page not found');
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).send('Internal server error');
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, () => {
  console.log('=========================================');
  console.log('  QR Emergency Alert System');
  console.log('=========================================');
  console.log(`  Server running on: http://localhost:${PORT}`);
  console.log(`  Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log('=========================================');
});

module.exports = app;
