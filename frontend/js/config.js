// Frontend API base configuration
// Set `window.API_BASE` to the backend base URL when hosting frontend separately.
// Default is empty string so relative `/api` works when backend serves frontend.
(function () {
  // For Netlify deployment, use the current origin
  window.API_BASE = window.API_BASE || window.location.origin;
})();
