document.addEventListener('DOMContentLoaded', function () {
  let video, stream, scanning = false, scanInterval;
  const cameraContainer = document.getElementById('cameraContainer');
  const toggleButton = document.getElementById('toggleCamera');
  const toggleText = document.getElementById('cameraToggleText');
  const scanStatus = document.getElementById('scanStatus');
  const restartBtn = document.getElementById('restartCamera');

  //  Toggle camera on/off
  toggleButton.addEventListener('click', function () {
    scanning ? stopCamera() : startCamera();
  });

  // Start camera
  function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(function (mediaStream) {
        stream = mediaStream;
        video = document.getElementById('video');
        video.srcObject = stream;
        video.play();

        cameraContainer.style.display = 'block';
        scanning = true;

        toggleText.textContent = 'Stop Camera';
        toggleButton.innerHTML = '<i class="bi bi-camera-video-off"></i> Stop Camera';
        toggleButton.classList.replace('btn-secondary-custom', 'btn-primary-red');

        startScanning();
      })
      .catch(function (err) {
        console.error('Camera access error:', err);
        scanStatus.innerHTML =
          '<small class="text-danger"><i class="bi bi-exclamation-triangle"></i> Camera access denied or not available</small>';
      });
  }

  //  Stop camera
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

    restartBtn.style.display = 'inline-block';
    toggleText.textContent = 'Start Camera';
    toggleButton.innerHTML = '<i class="bi bi-camera-video"></i> Start Camera';
    toggleButton.classList.replace('btn-primary-red', 'btn-secondary-custom');
  }

  //  Start scanning for QR codes
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
    }, 100);
  }

  //  Handle QR code logic
  function handleQRCode(qrData) {
    if (qrData.startsWith('{') && qrData.includes('certificate_serial')) {
      try {
        const parsed = JSON.parse(qrData);
        if (parsed.certificate_serial && parsed.donation_id) {
          scanStatus.innerHTML =
            '<small class="text-success"><i class="bi bi-check-circle"></i> Valid certificate QR detected!</small>';
          stopCamera();

          const manualInput = document.getElementById('qr_data');
          if (manualInput) {
            manualInput.value = qrData;
            const collapse = document.getElementById('manualInput');
            if (collapse) collapse.classList.add('show');
            manualInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            manualInput.focus();

            scanStatus.innerHTML =
              '<small class="text-success"><i class="bi bi-check-circle"></i> QR data copied below. Click "Verify Certificate" to proceed.</small>';
          }
        } else showWarning('Invalid certificate QR format');
      } catch {
        showWarning('Invalid QR code format');
      }
    } else showWarning('Not a certificate QR code');
  }

  //  Display warning messages
  function showWarning(msg) {
    scanStatus.innerHTML =
      `<small class="text-warning"><i class="bi bi-exclamation-triangle"></i> ${msg}</small>`;
    setTimeout(() => {
      scanStatus.innerHTML =
        '<small class="text-info"><i class="bi bi-search"></i> Scanning for QR codes...</small>';
    }, 2000);
  }

  // Restart camera
  restartBtn.addEventListener('click', function () {
    const manualInput = document.getElementById('qr_data');
    if (manualInput) manualInput.value = '';
    const collapse = document.getElementById('manualInput');
    if (collapse) collapse.classList.remove('show');
    restartBtn.style.display = 'none';
    startCamera();
  });

  window.addEventListener('beforeunload', stopCamera);
});
