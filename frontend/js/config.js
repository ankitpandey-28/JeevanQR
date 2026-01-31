// Frontend API base configuration
// Default is empty string so relative `/api` works when frontend and backend are on same origin.
(function () {
  'use strict';
  // Use empty string for same-origin deployment (Vercel, etc.)
  // This ensures all API calls go to the same domain the page is served from
  window.API_BASE = '';
})();
