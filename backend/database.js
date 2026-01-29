/**
 * QR Emergency Alert System - Database Module
 * Simple JSON file-based storage for users and accident logs
 */

const fs = require('fs');
const path = require('path');

// ============================================
// DATABASE CONFIGURATION
// ============================================

const DATABASE_DIR = path.join(__dirname, '..', 'database');
const USERS_FILE = path.join(DATABASE_DIR, 'users.json');
const LOGS_FILE = path.join(DATABASE_DIR, 'accident_logs.json');

// ============================================
// IN-MEMORY STORAGE
// ============================================

let users = {};          // token -> user object
let accidentLogs = [];   // Array of accident location logs

// ============================================
// INITIALIZATION
// ============================================

/**
 * Ensure database directory exists
 */
function ensureDatabaseDir() {
  if (!fs.existsSync(DATABASE_DIR)) {
    fs.mkdirSync(DATABASE_DIR, { recursive: true });
    console.log('[DB] Created database directory:', DATABASE_DIR);
  }
}

/**
 * Load users from JSON file
 */
function loadUsers() {
  try {
    if (fs.existsSync(USERS_FILE)) {
      const raw = fs.readFileSync(USERS_FILE, 'utf8');
      const parsed = JSON.parse(raw || '{}');
      if (parsed && typeof parsed === 'object') {
        users = parsed;
        console.log('[DB] Loaded', Object.keys(users).length, 'users from database');
      }
    }
  } catch (err) {
    console.error('[DB] Failed to load users.json:', err.message);
    users = {};
  }
}

/**
 * Load accident logs from JSON file
 */
function loadAccidentLogs() {
  try {
    if (fs.existsSync(LOGS_FILE)) {
      const raw = fs.readFileSync(LOGS_FILE, 'utf8');
      const parsed = JSON.parse(raw || '[]');
      if (Array.isArray(parsed)) {
        accidentLogs = parsed;
        console.log('[DB] Loaded', accidentLogs.length, 'accident logs');
      }
    }
  } catch (err) {
    console.error('[DB] Failed to load accident_logs.json:', err.message);
    accidentLogs = [];
  }
}

/**
 * Save users to JSON file
 */
function saveUsers() {
  try {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
  } catch (err) {
    console.error('[DB] Failed to save users.json:', err.message);
  }
}

/**
 * Save accident logs to JSON file
 */
function saveAccidentLogs() {
  try {
    fs.writeFileSync(LOGS_FILE, JSON.stringify(accidentLogs, null, 2), 'utf8');
  } catch (err) {
    console.error('[DB] Failed to save accident_logs.json:', err.message);
  }
}

// ============================================
// USER OPERATIONS
// ============================================

/**
 * Save a new user
 * @param {string} token - Unique token
 * @param {object} user - User data
 */
function saveUser(token, user) {
  users[token] = user;
  saveUsers();
  console.log('[DB] Saved user:', user.fullName, '(Token:', token.substring(0, 8) + '...)');
}

/**
 * Get user by token
 * @param {string} token - User token
 * @returns {object|null}
 */
function getUser(token) {
  return users[token] || null;
}

/**
 * Get all users (for admin)
 * @returns {object}
 */
function getAllUsers() {
  return users;
}

/**
 * Delete user by token
 * @param {string} token - User token
 * @returns {boolean}
 */
function deleteUser(token) {
  if (users[token]) {
    delete users[token];
    saveUsers();
    return true;
  }
  return false;
}

// ============================================
// ACCIDENT LOG OPERATIONS
// ============================================

/**
 * Log an accident location
 * @param {string} token - User token
 * @param {object} locationData - Location information
 */
function logAccidentLocation(token, locationData) {
  const logEntry = {
    id: Date.now(),
    token: token,
    ...locationData
  };
  
  accidentLogs.push(logEntry);
  saveAccidentLogs();
  
  console.log('[DB] Accident location logged for:', locationData.userName);
  console.log('     Location:', locationData.mapsUrl);
}

/**
 * Get recent accident logs
 * @param {number} limit - Maximum number of logs to return
 * @returns {array}
 */
function getRecentAccidentLogs(limit = 10) {
  return accidentLogs.slice(-limit).reverse();
}

// ============================================
// STATISTICS
// ============================================

/**
 * Get database statistics
 * @returns {object}
 */
function getStats() {
  return {
    totalUsers: Object.keys(users).length,
    totalAccidentLogs: accidentLogs.length,
    lastUpdated: new Date().toISOString()
  };
}

// ============================================
// INITIALIZE ON MODULE LOAD
// ============================================

ensureDatabaseDir();
loadUsers();
loadAccidentLogs();

// ============================================
// EXPORTS
// ============================================

module.exports = {
  // User operations
  saveUser,
  getUser,
  getAllUsers,
  deleteUser,
  
  // Accident log operations
  logAccidentLocation,
  getRecentAccidentLogs,
  
  // Statistics
  getStats
};
