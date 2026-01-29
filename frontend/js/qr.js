/**
 * QR Display Page JavaScript
 * Shows the generated QR code for download/print
 */

(function () {
  'use strict';

  /**
   * Get query parameter from URL
   * @param {string} name - Parameter name
   * @returns {string|null}
   */
  function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  }

  // DOM Elements
  const qrImage = document.getElementById('qrImage');
  const qrInfo = document.getElementById('qrInfo');

  // Get token from URL
  const token = getQueryParam('token');

  // API base (can be set by /js/config.js). Leave empty to use relative paths.
  const API_BASE = window.API_BASE || '';

  if (!token) {
    qrInfo.innerHTML =
      '<span class="error">Missing token. कृपया रजिस्ट्रेशन पेज से दोबारा आएं।</span>';
    qrImage.style.display = 'none';
  } else {
    const qrSrc = API_BASE + '/api/qr/' + encodeURIComponent(token);
    qrImage.src = qrSrc;
  }
})();
