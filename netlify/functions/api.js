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

// Override QRCode to work in serverless environment
const QRCode = require('qrcode');
const originalToFileStream = QRCode.toFileStream;
QRCode.toFileStream = function(res, text, options) {
  // Generate QR code as base64 data URL instead of stream
  return QRCode.toDataURL(text, options)
    .then(dataUrl => {
      // Extract base64 data from data URL
      const base64Data = dataUrl.replace(/^data:image\/png;base64,/, '');
      const buffer = Buffer.from(base64Data, 'base64');
      
      // Set proper headers
      res.setHeader('Content-Type', 'image/png');
      res.setHeader('Cache-Control', 'public, max-age=31536000');
      
      // Send the buffer directly
      res.send(buffer);
    })
    .catch(err => {
      throw err;
    });
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
  try {
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

    // Mock response object with proper async handling
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
        // Handle Buffer data (for QR codes)
        if (Buffer.isBuffer(data)) {
          responseData = data.toString('base64');
          headers['Content-Type'] = 'image/png';
          return {
            statusCode: statusCode,
            headers: headers,
            body: responseData,
            isBase64Encoded: true
          };
        }
      },
      end: function(data) {
        if (data) responseData = data;
      }
    };

    // Parse JSON body if present
    if (req.body && req.headers['content-type'] && req.headers['content-type'].includes('application/json')) {
      try {
        req.body = JSON.parse(req.body);
      } catch (e) {
        console.error('Failed to parse JSON body:', e);
      }
    }

    // Handle the request with Express app
    let result = await new Promise((resolve, reject) => {
      try {
        app(req, res);
        // Give more time for async operations
        setTimeout(() => {
          resolve({
            statusCode: statusCode,
            headers: headers,
            body: responseData || '',
            isBase64Encoded: false
          });
        }, 500);
      } catch (error) {
        console.error('Express app error:', error);
        reject(error);
      }
    });

    // Check if this is a QR code response (image/png content type)
    if (headers['Content-Type'] && headers['Content-Type'].includes('image/png')) {
      result.isBase64Encoded = true;
    }

    return result;

  } catch (error) {
    console.error('Netlify function error:', error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        error: 'Internal server error',
        details: error.message 
      }),
      isBase64Encoded: false
    };
  }
};
