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

  // API base - empty for same-origin requests
  const API_BASE = window.API_BASE || '';

  if (!token) {
    qrInfo.innerHTML =
      '<span class="error">Missing token. कृपया रजिस्ट्रेशन पेज से दोबारा आएं।</span>';
    qrImage.style.display = 'none';
  } else {
    const qrSrc = API_BASE + '/api/qr/' + encodeURIComponent(token);
    qrImage.src = qrSrc;
    
    // Add error handling for image load
    qrImage.onerror = function() {
      qrInfo.innerHTML =
        '<span class="error">Unable to load QR code. Please try again. QR लोड नहीं हो पाया।</span>';
      qrImage.style.display = 'none';
    };
    
    qrImage.onload = function() {
      qrInfo.innerHTML = `
        <p class="info-text">
          Long press on the QR image to download / save to your phone gallery.<br />
          QR इमेज को लंबा दबाकर अपने फोन में सेव करें।
        </p>
      `;
    };
  }
})();
