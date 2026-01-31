// Netlify serverless function handler
// This file handles Netlify Functions and forwards requests to the Express app

const app = require('../../backend/server');

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
