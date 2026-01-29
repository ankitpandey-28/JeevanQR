/**
 * Registration Page JavaScript
 * Handles user registration and QR generation
 */

(function () {
  'use strict';

  // DOM Elements
  const form = document.getElementById('registerForm');
  const messageEl = document.getElementById('message');
  const successEl = document.getElementById('success');
  const qrSection = document.getElementById('qrSection');
  const qrImage = document.getElementById('qrImage');
  const downloadLink = document.getElementById('downloadLink');
  const generateBtn = document.getElementById('generateBtn');
  const userNameDisplay = document.getElementById('userNameDisplay');
  const userBloodDisplay = document.getElementById('userBloodDisplay');

  /**
   * Show error message
   * @param {string} msg - Error message to display
   */
  function showError(msg) {
    messageEl.textContent = msg;
    messageEl.classList.remove('hidden');
  }

  /**
   * Hide all messages
   */
  function hideMessages() {
    messageEl.classList.add('hidden');
    successEl.classList.add('hidden');
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
   * Handle form submission
   * @param {Event} e - Form submit event
   */
  async function handleSubmit(e) {
    e.preventDefault();
    hideMessages();
    qrSection.classList.add('hidden');

    const fullName = document.getElementById('fullName').value.trim();
    const bloodGroup = document.getElementById('bloodGroup').value;
    const emergencyContact = document.getElementById('emergencyContact').value.trim();

    // Client-side validation
    if (!fullName || !bloodGroup || !emergencyContact) {
      showError('Please fill all fields. सभी जानकारी भरें।');
      return;
    }

    if (!isValidIndianPhone(emergencyContact)) {
      showError('Invalid phone number. कृपया सही फोन नंबर दें।');
      return;
    }

    // Disable button during request
    generateBtn.disabled = true;
    generateBtn.textContent = 'Please wait... / कृपया प्रतीक्षा करें...';

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fullName, bloodGroup, emergencyContact })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Failed to register user');
      }

      const data = await res.json();
      const { token, qrImageUrl } = data;

      // Display user info
      userNameDisplay.textContent = fullName;
      userBloodDisplay.textContent = 'Blood Group: ' + bloodGroup;

      // Show QR image
      const qrSrc = qrImageUrl + '?t=' + encodeURIComponent(token);
      qrImage.src = qrSrc;

      // Set download link
      downloadLink.href = qrSrc;

      qrSection.classList.remove('hidden');
      successEl.textContent = 'Emergency QR generated successfully. आपातकालीन QR बन गया है।';
      successEl.classList.remove('hidden');

      // Offer to open QR in full screen
      if (confirm('Open QR in full screen to save? क्या QR को फुल स्क्रीन में खोलें?')) {
        window.location.href = '/qr.html?token=' + encodeURIComponent(token);
      }
    } catch (err) {
      console.error('Registration error:', err);
      showError('Unable to generate QR. कृपया बाद में पुनः प्रयास करें।');
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerHTML = 'Generate Emergency QR<br />आपातकालीन QR बनाएं';
    }
  }

  // Initialize
  form.addEventListener('submit', handleSubmit);
})();
