// Vercel serverless handler that forwards requests to the Express app
// This file is optional because vercel.json already points to backend/server.js,
// but providing this explicit handler ensures compatibility.

const app = require('./backend/server');

module.exports = (req, res) => {
  return app(req, res);
};
