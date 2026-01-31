// Netlify serverless function handler
// This file handles Netlify Functions and forwards requests to the Express app

// Mock database for serverless environment (in-memory storage)
const mockDatabase = {
  users: {},
  accidentLogs: [],
  photos: {},
  
  saveUser: function(token, user) {
    this.users[token] = user;
    console.log('[MOCK DB] Saved user:', user.fullName);
  },
  
  getUser: function(token) {
    return this.users[token] || null;
  },
  
  logAccidentLocation: function(token, locationData) {
    const logEntry = {
      id: Date.now(),
      token: token,
      ...locationData
    };
    this.accidentLogs.push(logEntry);
    console.log('[MOCK DB] Accident location logged for:', locationData.userName);
  },
  
  logPhotoUpload: function(token, photoInfo) {
    this.photos[photoInfo.viewToken] = {
      ...photoInfo,
      token: token,
      viewed: false,
      createdAt: new Date().toISOString()
    };
    console.log('[MOCK DB] Photo uploaded:', photoInfo.filename);
  },
  
  getPhotoByViewToken: function(viewToken) {
    return this.photos[viewToken] || null;
  },
  
  markPhotoAsViewed: function(viewToken) {
    if (this.photos[viewToken]) {
      this.photos[viewToken].viewed = true;
      this.photos[viewToken].viewedAt = new Date().toISOString();
      console.log('[MOCK DB] Photo marked as viewed');
    }
  },
  
  getStats: function() {
    return {
      totalUsers: Object.keys(this.users).length,
      totalAccidentLogs: this.accidentLogs.length,
      totalPhotos: Object.keys(this.photos).length,
      lastUpdated: new Date().toISOString()
    };
  }
};

// Override the database module to use mock database
const originalRequire = require;
require = function(id) {
  if (id === './database') {
    return mockDatabase;
  }
  return originalRequire.apply(this, arguments);
};

// Override multer to work in serverless environment
const multer = require('multer');
const originalMulter = multer.single;
multer.single = function(fieldName) {
  return function(req, res, next) {
    // In serverless, we'll handle file uploads differently
    // For now, skip file upload functionality
    req.file = null;
    next();
  };
};

// Override fs operations for serverless
const fs = require('fs');
const originalMkdirSync = fs.mkdirSync;
const originalExistsSync = fs.existsSync;
fs.mkdirSync = function() { /* No-op in serverless */ };
fs.existsSync = function() { return false; };

const app = require('../../backend/server');

// Restore original require
require = originalRequire;

// Netlify Functions export handler
exports.handler = async (event, context) => {
  // Convert Netlify event to Express req/res format
  const req = {
    method: event.httpMethod,
    url: event.path,
    path: event.path,
    query: event.queryStringParameters || {},
    headers: event.headers || {},
    body: event.body ? (event.isBase64Encoded ? Buffer.from(event.body, 'base64').toString() : event.body) : null,
    protocol: 'https',
    get: function(header) {
      return this.headers[header.toLowerCase()];
    }
  };

  let responseData = '';
  let statusCode = 200;
  let headers = {
    'Content-Type': 'application/json'
  };

  // Mock response object
  const res = {
    status: function(code) {
      statusCode = code;
      return this;
    },
    setHeader: function(name, value) {
      headers[name] = value;
      return this;
    },
    json: function(data) {
      responseData = JSON.stringify(data);
      headers['Content-Type'] = 'application/json';
    },
    send: function(data) {
      responseData = data;
      if (typeof data === 'string' && !headers['Content-Type']) {
        headers['Content-Type'] = 'text/html';
      }
    },
    end: function(data) {
      if (data) responseData = data;
    }
  };

  // Handle the request with Express app
  await new Promise((resolve) => {
    app(req, res);
    // Give some time for async operations
    setTimeout(resolve, 100);
  });

  // Return Netlify response format
  return {
    statusCode: statusCode,
    headers: headers,
    body: responseData,
    isBase64Encoded: false
  };
};
