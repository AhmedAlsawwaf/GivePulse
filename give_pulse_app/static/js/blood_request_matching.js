document.addEventListener("DOMContentLoaded", function () {
  console.log("Blood request matching script loaded!");
  
  // 🩸 Blood Request Matching with AJAX
  const matchButton = document.getElementById("match-blood-request-btn");
  const matchForm = document.getElementById("match-blood-request-form");
  
  console.log("Match button found:", matchButton);
  console.log("Match form found:", matchForm);
  
  if (matchButton && matchForm) {
    console.log("Setting up click handler...");
    matchButton.addEventListener("click", async function (e) {
      e.preventDefault();
      console.log("Button clicked!");
      
      // Get the request ID from the form action or data attribute
      const requestId = matchForm.getAttribute("data-request-id") || 
                       matchForm.action.match(/\/requests\/(\d+)\/match/)?.[1];
      
      console.log("Request ID:", requestId);
      console.log("CSRF Token:", getCSRFToken());
      
      if (!requestId) {
        showMessage("Error: Could not determine request ID", "error");
        return;
      }
      
      // Disable button and show loading state
      const originalText = matchButton.textContent;
      matchButton.disabled = true;
      matchButton.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Matching';
      
      try {
        console.log("Sending AJAX request...");
        
        const response = await fetch(`/requests/${requestId}/match-ajax/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
            "Accept": "application/json"
          }
        });
        
        console.log("Response received:", response.status);
        
        // Check if response is ok
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseText = await response.text();
        console.log("Raw response text:", responseText);
        
        let data;
        try {
          data = JSON.parse(responseText);
          console.log("Parsed JSON data:", data);
        } catch (jsonError) {
          console.error("JSON parsing error:", jsonError);
          console.error("Response text:", responseText);
          throw new Error("Invalid JSON response from server");
        }
        
        if (data && data.success) {
          // Success - show success message and update UI
          showMessage(data.message, "success");
          
          // Update button to show matched state
          matchButton.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Matched!';
          matchButton.classList.remove("btn-primary-red");
          matchButton.classList.add("btn-success");
          
          // Optionally hide the button or make it non-clickable
          matchButton.disabled = true;
          
          // Update any status indicators on the page
          updateMatchStatus(true);
          
        } else {
          // Error - show error message
          const errorMsg = (data && data.error) ? data.error : "Failed to match blood request";
          showMessage(errorMsg, "error");
          
          // Re-enable button
          matchButton.disabled = false;
          matchButton.textContent = originalText;
        }
        
      } catch (error) {
        console.error("Error matching blood request:", error);
        
        let errorMessage = "Network error. Please try again.";
        if (error.message.includes('HTTP error')) {
          errorMessage = `Server error: ${error.message}`;
        } else if (error.message.includes('JSON')) {
          errorMessage = "Server returned invalid response";
        }
        
        showMessage(errorMessage, "error");
        
        // Re-enable button
        matchButton.disabled = false;
        matchButton.textContent = originalText;
      }
    });
  }
  
  // Helper function to get CSRF token
  function getCSRFToken() {
    // Try multiple ways to get CSRF token
    let token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    // Try from meta tag
    token = document.querySelector('meta[name="csrf-token"]');
    if (token) return token.getAttribute('content');
    
    // Try from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') return value;
    }
    
    console.warn('CSRF token not found');
    return '';
  }
  
  // Helper function to show messages
  function showMessage(message, type) {
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.ajax-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show ajax-message`;
    messageDiv.innerHTML = `
      <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-1"></i>
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert message at the top of the content area
    const contentArea = document.querySelector('.container') || document.body;
    contentArea.insertBefore(messageDiv, contentArea.firstChild);
    
    // Auto-dismiss success messages after 5 seconds
    if (type === 'success') {
      setTimeout(() => {
        if (messageDiv.parentNode) {
          messageDiv.remove();
        }
      }, 5000);
    }
  }
  
  // Helper function to update match status indicators
  function updateMatchStatus(isMatched) {
    // Update any status badges or indicators
    const statusBadges = document.querySelectorAll('.match-status');
    statusBadges.forEach(badge => {
      if (isMatched) {
        badge.textContent = 'Matched';
        badge.className = 'badge bg-success match-status';
      }
    });
    
    // Update any "already matched" indicators
    const alreadyMatched = document.getElementById('already-matched');
    if (alreadyMatched) {
      alreadyMatched.style.display = isMatched ? 'block' : 'none';
    }
  }
});
