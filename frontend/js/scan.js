/**
 * Emergency Scan Page JavaScript
 * Handles emergency contact calls, helplines, and location sharing
 */

(function () {
  'use strict';

  // ============================================
  // UTILITY FUNCTIONS
  // ============================================

  /**
   * Extract token from URL path
   * @returns {string}
   */
  function getTokenFromPath() {
    const parts = window.location.pathname.split('/');
    return parts[parts.length - 1] || '';
  }

  /**
   * Decode base64 encoded contact
   * @param {string} encoded - Base64 encoded string
   * @returns {string|null}
   */
  function decodeContact(encoded) {
    try {
      return atob(encoded);
    } catch (e) {
      return null;
    }
  }

  // ============================================
  // DOM ELEMENTS
  // ============================================

  const personNameEl = document.getElementById('personName');
  const personBloodEl = document.getElementById('personBlood');
  const loadErrorEl = document.getElementById('loadError');
  const callPersonalBtn = document.getElementById('callPersonalBtn');
  const locationBtn = document.getElementById('locationBtn');
  const locationStatus = document.getElementById('locationStatus');
  const locationBox = document.getElementById('locationBox');
  const shareLocationBtn = document.getElementById('shareLocationBtn');

  // ============================================
  // STATE
  // ============================================

  const token = getTokenFromPath();
  let contactEncoded = null;
  let mapsUrl = null;

  // ============================================
  // API FUNCTIONS
  // ============================================

  /**
   * Load public user data from API
   */
  async function loadPublicData() {
    try {
      const res = await fetch('/api/users/' + encodeURIComponent(token) + '/public');
      
      if (!res.ok) {
        throw new Error('Not found');
      }
      
      const data = await res.json();

      personNameEl.textContent = data.fullName;
      personBloodEl.textContent = 'Blood Group: ' + data.bloodGroup;
      contactEncoded = data.contactEncoded;
    } catch (err) {
      console.error('Failed to load user data:', err);
      personNameEl.textContent = 'QR not valid';
      personBloodEl.textContent = '';
      loadErrorEl.textContent = 'Unable to load details. QR मान्य नहीं है या डेटा नहीं मिला।';
      loadErrorEl.classList.remove('hidden');
      callPersonalBtn.disabled = true;
      locationBtn.disabled = true;
    }
  }

  /**
   * Log location to backend (non-blocking)
   * @param {number} latitude
   * @param {number} longitude
   * @param {string} mapsUrl
   */
  function logLocationToBackend(latitude, longitude, mapsUrl) {
    try {
      fetch('/api/users/' + encodeURIComponent(token) + '/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude, longitude, mapsUrl })
      });
    } catch (e) {
      // Ignore errors - this is non-critical logging
    }
  }

  // ============================================
  // EVENT HANDLERS
  // ============================================

  /**
   * Handle emergency contact call button click
   */
  function handleCallEmergencyContact() {
    if (!contactEncoded) {
      alert('Emergency contact not available. आपातकालीन संपर्क उपलब्ध नहीं है।');
      return;
    }

    const number = decodeContact(contactEncoded);
    
    if (!number) {
      alert('Unable to use contact number. नंबर उपयोग नहीं हो सका।');
      return;
    }

    // Trigger phone dialer (number not shown on page)
    window.location.href = 'tel:' + encodeURIComponent(number);
  }

  /**
   * Handle location button click
   */
  function handleGetLocation() {
    if (!navigator.geolocation) {
      locationStatus.textContent = 
        'Location not supported on this device. यह डिवाइस लोकेशन सपोर्ट नहीं करता।';
      return;
    }

    locationStatus.textContent = 'Getting GPS location... GPS लोकेशन ली जा रही है...';

    navigator.geolocation.getCurrentPosition(
      // Success callback
      function (pos) {
        const { latitude, longitude } = pos.coords;
        
        mapsUrl = 'https://www.google.com/maps?q=' + 
          encodeURIComponent(latitude + ',' + longitude);

        locationBox.textContent = mapsUrl;
        locationBox.classList.remove('hidden');
        locationStatus.textContent = 
          'Copy or share this link with emergency contact. इस लिंक को आपातकालीन संपर्क के साथ साझा करें।';
        shareLocationBtn.classList.remove('hidden');

        // Log to backend (fire-and-forget)
        logLocationToBackend(latitude, longitude, mapsUrl);
      },
      // Error callback
      function (err) {
        console.error('Geolocation error:', err);
        locationStatus.textContent = 
          'Could not get location. कृपया लोकेशन परमिशन दें या फिर से प्रयास करें।';
      },
      // Options
      {
        enableHighAccuracy: false,
        timeout: 8000,
        maximumAge: 0
      }
    );
  }

  /**
   * Handle share location button click
   */
  async function handleShareLocation() {
    if (!mapsUrl) return;

    const text = 'Accident location: ' + mapsUrl + '\nदुर्घटना स्थान (लोकेशन लिंक)।';

    // Try Web Share API first (native share sheet)
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Accident Location',
          text: text
        });
        return;
      } catch (e) {
        // User cancelled or share failed, try clipboard
      }
    }

    // Fallback to clipboard
    if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        alert('Location copied. Paste in SMS / WhatsApp to share.\nलोकेशन कॉपी हो गई है। SMS / WhatsApp में पेस्ट करें।');
        return;
      } catch (e) {
        // Clipboard failed
      }
    }

    // Final fallback
    alert('Please long press on the link and copy it to share.\nकृपया लिंक को लंबे समय तक दबाकर कॉपी करें और शेयर करें।');
  }

  // ============================================
  // INITIALIZE
  // ============================================

  callPersonalBtn.addEventListener('click', handleCallEmergencyContact);
  locationBtn.addEventListener('click', handleGetLocation);
  shareLocationBtn.addEventListener('click', handleShareLocation);

  // Load data on page load
  loadPublicData();
})();
