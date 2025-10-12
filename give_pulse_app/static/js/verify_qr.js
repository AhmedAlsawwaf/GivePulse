document.addEventListener('DOMContentLoaded', function() {
  const video = document.getElementById('video');
  const cameraContainer = document.getElementById('cameraContainer');
  const toggleButton = document.getElementById('toggleCamera');
  const toggleText = document.getElementById('cameraToggleText');
  const scanStatus = document.getElementById('scanStatus');
  const restartButton = document.getElementById('restartCamera');
  let stream = null;
  let scanning = false;
  let scanInterval = null;

  // Toggle camera on/off
  toggleButton.addEventListener('click', () => {
    scanning ? stopCamera() : startCamera();
  });

  // Start camera
  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });

      video.srcObject = stream;
      await video.play();
      cameraContainer.style.display = 'block';
      scanning = true;

      toggleText.textContent = 'Stop Camera';
      toggleButton.classList.replace('btn-secondary-custom', 'btn-primary-red');
      startScanning();
    } catch (err) {
      console.error('Camera access error:', err);
      scanStatus.innerHTML = `
        <small class="text-danger">
          <i class="bi bi-exclamation-triangle"></i>
          Unable to access camera. Please use manual input.
        </small>`;
      scanStatus.className = 'mt-1 error';
    }
  }

  // Stop camera
  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    if (scanInterval) {
      clearInterval(scanInterval);
      scanInterval = null;
    }
    cameraContainer.style.display = 'none';
    scanning = false;

    toggleText.textContent = 'Start Camera';
    toggleButton.classList.replace('btn-primary-red', 'btn-secondary-custom');
    restartButton.style.display = 'inline-block';
  }

  // Start scanning loop
  function startScanning() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    scanInterval = setInterval(() => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        if (code) handleQRCode(code.data.trim());
      }
    }, 200);
  }

  // Process detected QR
  function handleQRCode(data) {
    if (data.startsWith('{') && data.includes('appointment_id')) {
      try {
        const parsed = JSON.parse(data);
        if (parsed.appointment_id) {
          stopCamera();
          const input = document.getElementById('qr_data');
          input.value = data;
          document.getElementById('manualInput').classList.add('show');
          input.scrollIntoView({ behavior: 'smooth', block: 'center' });

          scanStatus.innerHTML = `
            <small class="text-success">
              <i class="bi bi-check-circle"></i>
              Valid QR detected — ready to verify.
            </small>`;
          scanStatus.className = 'mt-1 success';
        }
      } catch {
        invalidQR('Invalid JSON format in QR code');
      }
    } else {
      invalidQR('Not a valid GivePulse appointment QR code');
    }
  }

  // Restart camera
  restartButton?.addEventListener('click', () => {
    document.getElementById('qr_data').value = '';
    document.getElementById('manualInput').classList.remove('show');
    restartButton.style.display = 'none';
    startCamera();
  });

  // Handle invalid QR feedback
  function invalidQR(message) {
    scanStatus.innerHTML = `
      <small class="text-danger">
        <i class="bi bi-x-circle"></i> ${message}
      </small>`;
    scanStatus.className = 'mt-1 error';
    setTimeout(() => {
      scanStatus.innerHTML = `
        <small class="text-info">
          <i class="bi bi-search"></i> Scanning for QR codes...
        </small>`;
      scanStatus.className = 'mt-1';
    }, 2000);
  }

  // Stop camera when leaving page
  window.addEventListener('beforeunload', stopCamera);
});
