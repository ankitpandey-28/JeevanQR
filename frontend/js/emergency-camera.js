/**
 * Camera Service for Emergency Photo Capture
 * Handles photo capture, upload, and secure sharing
 */

class EmergencyCameraService {
  constructor() {
    this.photoData = null;
    this.photoUrl = null;
    this.isPhotoShared = false;
  }

  /**
   * Check if camera is available
   */
  isCameraAvailable() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  /**
   * Request camera permission
   */
  async requestCameraPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', // Use back camera
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      // Stop the stream immediately (just checking permission)
      stream.getTracks().forEach(track => track.stop());
      return { success: true };
    } catch (error) {
      console.error('Camera permission error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Capture photo from camera
   */
  async capturePhoto() {
    return new Promise((resolve, reject) => {
      if (!this.isCameraAvailable()) {
        reject(new Error('Camera not available on this device'));
        return;
      }

      navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      })
      .then(stream => {
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();

        video.onloadedmetadata = () => {
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          
          const context = canvas.getContext('2d');
          context.drawImage(video, 0, 0);
          
          // Stop camera stream
          stream.getTracks().forEach(track => track.stop());
          
          // Convert to blob and data URL
          canvas.toBlob((blob) => {
            this.photoData = blob;
            this.photoUrl = canvas.toDataURL('image/jpeg', 0.8);
            resolve({
              success: true,
              photoUrl: this.photoUrl,
              photoData: blob
            });
          }, 'image/jpeg', 0.8);
        };
      })
      .catch(error => {
        reject(error);
      });
    });
  }

  /**
   * Upload photo to server and get secure URL
   */
  async uploadPhoto(token, patientName) {
    if (!this.photoData) {
      throw new Error('No photo data to upload');
    }

    const formData = new FormData();
    formData.append('photo', this.photoData, `emergency-${Date.now()}.jpg`);
    formData.append('token', token);
    formData.append('patientName', patientName);
    formData.append('timestamp', new Date().toISOString());

    try {
      const response = await fetch('/api/upload-photo', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload photo');
      }

      const result = await response.json();
      return {
        success: true,
        photoUrl: result.photoUrl,
        secureUrl: result.secureUrl,
        viewToken: result.viewToken
      };
    } catch (error) {
      throw new Error(`Photo upload failed: ${error.message}`);
    }
  }

  /**
   * Generate photo sharing message
   */
  generatePhotoMessage(patientName, photoUrl, secureUrl) {
    return `🚨 EMERGENCY ALERT - ACCIDENT PHOTO 🚨
Patient: ${patientName}
Location: See attached photo
Time: ${new Date().toLocaleString()}

📸 Accident Photo: ${secureUrl}
⚠️ This photo will self-destruct in 24 hours

View photo securely: ${secureUrl}`;
  }

  /**
   * Share photo to all emergency contacts
   */
  async sharePhotoToAllContacts(patientName, contacts, photoUrl, secureUrl) {
    const message = this.generatePhotoMessage(patientName, photoUrl, secureUrl);
    const isOnline = navigator.onLine;
    
    if (isOnline) {
      return await this.sharePhotoOnline(patientName, contacts, message, photoUrl);
    } else {
      return await this.sharePhotoSMS(patientName, contacts, message);
    }
  }

  /**
   * Share photo via WhatsApp (online)
   */
  async sharePhotoOnline(patientName, contacts, message, photoUrl) {
    const results = [];
    
    for (let i = 0; i < contacts.length; i++) {
      const contact = contacts[i];
      try {
        // WhatsApp doesn't support direct image sharing via URL
        // So we share the secure link to view the photo
        const whatsappUrl = `https://wa.me/${contact.phone.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`;
        
        window.open(whatsappUrl, '_blank');
        results.push({ contact: contact.name, method: 'WhatsApp', status: 'opened' });
        
        // Small delay between openings
        if (i < contacts.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        results.push({ contact: contact.name, method: 'WhatsApp', status: 'failed', error: error.message });
      }
    }
    
    return {
      success: true,
      method: 'WhatsApp Photo Sharing',
      results: results,
      message: `Photo shared with ${results.filter(r => r.status === 'opened').length} contacts`
    };
  }

  /**
   * Share photo via SMS (offline)
   */
  async sharePhotoSMS(patientName, contacts, message) {
    const results = [];
    
    for (let i = 0; i < contacts.length; i++) {
      const contact = contacts[i];
      try {
        const smsUrl = `sms:${contact.phone}?body=${encodeURIComponent(message)}`;
        
        window.open(smsUrl, '_blank');
        results.push({ contact: contact.name, method: 'SMS', status: 'opened' });
        
        // Small delay between SMS
        if (i < contacts.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } catch (error) {
        results.push({ contact: contact.name, method: 'SMS', status: 'failed', error: error.message });
      }
    }
    
    return {
      success: true,
      method: 'SMS Photo Sharing',
      results: results,
      message: `Photo shared via SMS to ${results.filter(r => r.status === 'opened').length} contacts`
    };
  }

  /**
   * Complete photo capture and sharing workflow
   */
  async captureAndSharePhoto(token, patientName, contacts) {
    try {
      // Step 1: Check camera permission
      const permission = await this.requestCameraPermission();
      if (!permission.success) {
        throw new Error(`Camera permission denied: ${permission.error}`);
      }

      // Step 2: Capture photo
      const captureResult = await this.capturePhoto();
      if (!captureResult.success) {
        throw new Error('Failed to capture photo');
      }

      // Step 3: Upload photo
      const uploadResult = await this.uploadPhoto(token, patientName);
      if (!uploadResult.success) {
        throw new Error('Failed to upload photo');
      }

      // Step 4: Share photo
      const shareResult = await this.sharePhotoToAllContacts(
        patientName, 
        contacts, 
        uploadResult.photoUrl, 
        uploadResult.secureUrl
      );

      this.isPhotoShared = true;

      return {
        success: true,
        photoUrl: uploadResult.photoUrl,
        secureUrl: uploadResult.secureUrl,
        viewToken: uploadResult.viewToken,
        shareResult: shareResult
      };

    } catch (error) {
      throw new Error(`Photo capture and sharing failed: ${error.message}`);
    }
  }

  /**
   * Clear photo data
   */
  clearPhoto() {
    this.photoData = null;
    this.photoUrl = null;
    this.isPhotoShared = false;
  }
}

// Export for use in other files
window.EmergencyCameraService = EmergencyCameraService;
