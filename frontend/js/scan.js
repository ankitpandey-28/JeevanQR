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
  const emergencyContactsListEl = document.getElementById('emergencyContactsList');
  const governmentHelplinesListEl = document.getElementById('governmentHelplinesList');
  const loadErrorEl = document.getElementById('loadError');
  const cameraBtn = document.getElementById('cameraBtn');
  const cameraStatus = document.getElementById('cameraStatus');
  const cameraPreview = document.getElementById('cameraPreview');
  const cameraVideo = document.getElementById('cameraVideo');
  const captureBtn = document.getElementById('captureBtn');
  const cancelCameraBtn = document.getElementById('cancelCameraBtn');
  const photoResult = document.getElementById('photoResult');
  const capturedPhoto = document.getElementById('capturedPhoto');
  const photoStatus = document.getElementById('photoStatus');
  const locationBtn = document.getElementById('locationBtn');
  const locationStatus = document.getElementById('locationStatus');
  const locationBox = document.getElementById('locationBox');
  const sharingProgress = document.getElementById('sharingProgress');
  const progressStatus = document.getElementById('progressStatus');
  const sharingResults = document.getElementById('sharingResults');
  const resultsList = document.getElementById('resultsList');
  const connectivityStatus = document.getElementById('connectivityStatus');

  // ============================================
  // STATE
  // ============================================

  const token = getTokenFromPath();
  let contactEncoded = null;
  let mapsUrl = null;
  let patientData = null;
  let locationService = null;
  let cameraService = null;

  // ============================================
  // API FUNCTIONS
  // ============================================

  // API base (can be set by /js/config.js). Leave empty to use relative paths.
  const API_BASE = window.API_BASE || '';

  /**
   * Load public user data from API
   */
  async function loadPublicData() {
    try {
      console.log('Loading data for token:', token);
      console.log('API request URL:', API_BASE + '/api/users/' + encodeURIComponent(token) + '/public');
      
      const res = await fetch(API_BASE + '/api/users/' + encodeURIComponent(token) + '/public');
      
      console.log('Response status:', res.status);
      console.log('Response ok:', res.ok);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      console.log('Received data:', data);
      patientData = data;

      personNameEl.textContent = data.fullName;
      personBloodEl.textContent = 'Blood Group: ' + data.bloodGroup;

      // Display emergency contacts
      emergencyContactsListEl.innerHTML = '';
      data.emergencyContacts.forEach((contact, index) => {
        const contactDiv = document.createElement('div');
        contactDiv.className = 'contact-item';
        contactDiv.innerHTML = `
          <button class="btn-large btn-call" onclick="callContact('${contact.phoneEncoded}')">
            📞 Call ${contact.name}<br />
            📞 ${contact.name} को कॉल करें
          </button>
        `;
        emergencyContactsListEl.appendChild(contactDiv);
      });

      // Display government helplines
      governmentHelplinesListEl.innerHTML = '';
      data.governmentHelplines.forEach((helpline) => {
        const helplineDiv = document.createElement('div');
        helplineDiv.className = 'helpline-item';
        helplineDiv.innerHTML = `
          <button class="btn-large btn-helpline" onclick="window.location.href='tel:${helpline.number}'">
            🚨 Call ${helpline.name}<br />
            🚨 ${helpline.name}: ${helpline.number}
          </button>
        `;
        governmentHelplinesListEl.appendChild(helplineDiv);
      });

      // Initialize location sharing service
      locationService = new LocationSharingService();
      
      // Initialize camera service
      cameraService = new EmergencyCameraService();
      updateConnectivityStatus();

    } catch (err) {
      console.error('Failed to load user data:', err);
      console.error('Error details:', err.message);
      console.error('Token used:', token);
      
      personNameEl.textContent = 'QR not valid';
      personBloodEl.textContent = '';
      emergencyContactsListEl.innerHTML = '';
      governmentHelplinesListEl.innerHTML = '';
      loadErrorEl.textContent = `Unable to load details. ${err.message}`;
      loadErrorEl.classList.remove('hidden');
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
      fetch(API_BASE + '/api/users/' + encodeURIComponent(token) + '/location', {
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
   * Handle camera button click
   */
  async function handleCameraClick() {
    if (!cameraService) {
      cameraStatus.textContent = 'Camera service not available. कैमरा सेवा उपलब्ध नहीं है।';
      return;
    }

    // Check camera availability
    if (!cameraService.isCameraAvailable()) {
      cameraStatus.textContent = 'Camera not available on this device. इस डिवाइस पर कैमरा उपलब्ध नहीं है।';
      return;
    }

    // Request camera permission
    const permission = await cameraService.requestCameraPermission();
    if (!permission.success) {
      cameraStatus.textContent = `Camera permission denied: ${permission.error}`;
      return;
    }

    // Show camera preview
    cameraStatus.textContent = 'Camera ready! Position to capture accident scene. कैमरा तैयार! दुर्घटना दृश्य कैप्चर करने के लिए स्थित करें।';
    cameraPreview.classList.remove('hidden');
    cameraBtn.classList.add('hidden');

    // Start camera stream
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      cameraVideo.srcObject = stream;
      cameraVideo.play();
      
    } catch (error) {
      console.error('Camera error:', error);
      cameraStatus.textContent = `Camera error: ${error.message}`;
      cameraPreview.classList.add('hidden');
      cameraBtn.classList.remove('hidden');
    }
  }

  /**
   * Handle photo capture
   */
  async function handleCapturePhoto() {
    if (!cameraService || !patientData) {
      cameraStatus.textContent = 'Service not ready. कृपया प्रतीक्षा करें।';
      return;
    }

    try {
      cameraStatus.textContent = 'Capturing photo... फोटो कैप्चर रही है...';
      captureBtn.disabled = true;

      // Capture photo
      const result = await cameraService.capturePhoto();
      if (!result.success) {
        throw new Error('Failed to capture photo');
      }

      // Show captured photo
      capturedPhoto.src = result.photoUrl;
      photoResult.classList.remove('hidden');
      cameraPreview.classList.add('hidden');

      // Upload and share photo
      cameraStatus.textContent = 'Uploading and sharing photo... फोटो अपलोड और साझा कर रहे हैं...';
      
      const uploadResult = await cameraService.uploadPhoto(token, patientData.fullName);
      if (!uploadResult.success) {
        throw new Error('Failed to upload photo');
      }

      // Share photo with all contacts
      const shareResult = await cameraService.sharePhotoToAllContacts(
        patientData.fullName,
        patientData.emergencyContacts,
        uploadResult.photoUrl,
        uploadResult.secureUrl
      );

      // Show results
      photoStatus.innerHTML = `
        ✅ Photo captured and shared successfully!<br>
        📤 Shared with ${shareResult.results.filter(r => r.status === 'opened').length} emergency contacts<br>
        🔗 Secure link: ${uploadResult.secureUrl}<br>
        ⚠️ One-time access only
      `;

      // Clean up camera
      if (cameraVideo.srcObject) {
        cameraVideo.srcObject.getTracks().forEach(track => track.stop());
      }

      cameraService.clearPhoto();

    } catch (error) {
      console.error('Photo capture error:', error);
      cameraStatus.textContent = `❌ Photo capture failed: ${error.message}`;
      
      // Clean up camera
      if (cameraVideo.srcObject) {
        cameraVideo.srcObject.getTracks().forEach(track => track.stop());
      }
    } finally {
      captureBtn.disabled = false;
    }
  }

  /**
   * Handle camera cancel
   */
  function handleCancelCamera() {
    // Stop camera stream
    if (cameraVideo.srcObject) {
      cameraVideo.srcObject.getTracks().forEach(track => track.stop());
    }

    // Hide preview, show button
    cameraPreview.classList.add('hidden');
    cameraBtn.classList.remove('hidden');
    photoResult.classList.add('hidden');
    cameraStatus.textContent = '';
    
    // Clear camera service
    if (cameraService) {
      cameraService.clearPhoto();
    }
  }

  /**
   * Handle emergency contact call button click
   * @param {string} encodedPhone - Base64 encoded phone number
   */
  function callContact(encodedPhone) {
    const number = decodeContact(encodedPhone);
    
    if (!number) {
      alert('Unable to use contact number. नंबर उपयोग नहीं हो सका।');
      return;
    }

    // Trigger phone dialer (number not shown on page)
    window.location.href = 'tel:' + encodeURIComponent(number);
  }

  /**
   * Update connectivity status display
   */
  function updateConnectivityStatus() {
    if (!locationService) return;
    
    const isOnline = locationService.checkConnectivity();
    connectivityStatus.textContent = isOnline 
      ? '🌐 Online - Internet available / इंटरनेट उपलब्ध'
      : '📱 Offline - No internet / इंटरनेट नहीं';
    connectivityStatus.className = isOnline ? 'info-text success-text' : 'info-text warning-text';
  }
  async function handleGetLocation() {
    if (!locationService || !patientData) {
      locationStatus.textContent = 'Service not ready. कृपया प्रतीक्षा करें।';
      return;
    }

    async function handleGetLocation() {
    if (!locationService || !patientData) {
      locationStatus.textContent = 'Service not ready. कृपया प्रतीक्षा करें।';
      return;
    }

    locationStatus.textContent = 'Getting GPS location... GPS लोकेशन ली जा रही है...';
    sharingProgress.classList.add('hidden');
    sharingResults.classList.add('hidden');
    locationBox.classList.add('hidden');

    try {
      // Show progress
      sharingProgress.classList.remove('hidden');
      progressStatus.textContent = '📍 Acquiring GPS coordinates...';

      const location = await locationService.getCurrentLocation();
      const formattedLocation = locationService.getFormattedLocation();
      
      locationBox.innerHTML = `
        <strong>📍 Location Found:</strong><br>
        Coordinates: ${formattedLocation.coordinates}<br>
        Accuracy: ${formattedLocation.accuracy}<br>
        Time: ${formattedLocation.time}
      `;
      locationBox.classList.remove('hidden');
      
      progressStatus.textContent = '📤 Sharing location to all emergency contacts...';

      // Auto-share to all contacts
      const result = await locationService.shareLocation(
        patientData.fullName, 
        patientData.emergencyContacts,
        'auto'
      );
      
      // Hide progress, show results
      sharingProgress.classList.add('hidden');
      sharingResults.classList.remove('hidden');
      
      // Display results
      resultsList.innerHTML = '';
      if (result.results) {
        result.results.forEach(contactResult => {
          const statusIcon = contactResult.status === 'opened' ? '✅' : '❌';
          const resultDiv = document.createElement('div');
          resultDiv.className = 'result-item';
          resultDiv.innerHTML = `
            ${statusIcon} ${contactResult.name} - ${contactResult.method}
            ${contactResult.error ? `<br><small>Error: ${contactResult.error}</small>` : ''}
          `;
          resultsList.appendChild(resultDiv);
        });
      } else {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        resultDiv.innerHTML = `✅ ${result.message}`;
        resultsList.appendChild(resultDiv);
      }
      
      locationStatus.textContent = `✅ Location shared successfully! / स्थान सफलतापूर्वक साझा किया गया!`;

      // Log to backend
      logLocationToBackend(location.latitude, location.longitude, location.mapsUrl);

    } catch (error) {
      console.error('Location error:', error);
      sharingProgress.classList.add('hidden');
      locationStatus.textContent = `❌ Could not share location: ${error.message}`;
    }
  }

  /**
   * Handle online sharing
   */
  async function handleShareOnline() {
    if (!locationService || !patientData) return;

    try {
      const result = await locationService.shareLocationOnline(
        patientData.fullName, 
        patientData.emergencyContacts
      );
      
      alert(`Location shared successfully via ${result.method}! / स्थान सफलतापूर्वक साझा किया गया!`);
      
    } catch (error) {
      console.error('Online sharing error:', error);
      alert(`Online sharing failed: ${error.message}\nऑनलाइन साझाकरण विफल: ${error.message}`);
    }
  }

  /**
   * Handle SMS sharing
   */
  function handleShareSMS() {
    if (!locationService || !patientData) return;

    try {
      const result = locationService.shareLocationViaSMS(
        patientData.fullName, 
        patientData.emergencyContacts
      );
      
      // Display SMS links
      smsLinks.innerHTML = '';
      result.links.forEach(link => {
        const smsBtn = document.createElement('button');
        smsBtn.className = 'btn-large btn-secondary';
        smsBtn.innerHTML = `
          📱 Send SMS to ${link.name}<br>
          📱 ${link.name} को SMS भेजें
        `;
        smsBtn.onclick = () => window.location.href = link.smsUrl;
        smsLinks.appendChild(smsBtn);
      });
      
      smsOptions.classList.remove('hidden');
      locationStatus.textContent = 'Click contacts to send SMS. संपर्कों पर क्लिक करके SMS भेजें।';

    } catch (error) {
      console.error('SMS sharing error:', error);
      alert(`SMS sharing failed: ${error.message}\nSMS साझाकरण विफल: ${error.message}`);
    }
  }

  /**
   * Handle share location button click (legacy)
   */
  async function handleShareLocation() {
    if (!locationService || !patientData) return;

    try {
      const result = await locationService.shareLocation(
        patientData.fullName, 
        patientData.emergencyContacts,
        'auto'
      );
      
      alert(`Location shared via ${result.method}! / स्थान साझा किया गया!`);
      
    } catch (error) {
      console.error('Location sharing error:', error);
      alert(`Location sharing failed: ${error.message}\nस्थान साझाकरण विफल: ${error.message}`);
    }
  }

  // ============================================
  // INITIALIZE
  // ============================================

  // Make callContact globally accessible
  window.callContact = callContact;

  // Event listeners
  cameraBtn.addEventListener('click', handleCameraClick);
  captureBtn.addEventListener('click', handleCapturePhoto);
  cancelCameraBtn.addEventListener('click', handleCancelCamera);
  locationBtn.addEventListener('click', handleGetLocation);

  // Listen for connectivity changes
  window.addEventListener('online', updateConnectivityStatus);
  window.addEventListener('offline', updateConnectivityStatus);

  // Load data on page load
  loadPublicData();
})();
