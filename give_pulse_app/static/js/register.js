// Prevent multiple initializations
let passwordTogglesInitialized = false;

function initPasswordToggles() {
  if (passwordTogglesInitialized) {
    return;
  }
  
  const toggles = document.querySelectorAll(".toggle-password");
  
  if (toggles.length === 0) {
    return;
  }
  
  toggles.forEach((toggle) => {
    const targetId = toggle.getAttribute("data-target");
    const input = document.getElementById(targetId);

    if (!input) {
      return;
    }

    // Check if already has click listener
    if (toggle.hasAttribute('data-toggle-initialized')) {
      return;
    }

    // Mark as initialized
    toggle.setAttribute('data-toggle-initialized', 'true');
    
    // Add click listener
    toggle.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      if (input.type === "password") {
        input.type = "text";
        toggle.classList.remove("bi-eye");
        toggle.classList.add("bi-eye-slash", "active");
      } else {
        input.type = "password";
        toggle.classList.remove("bi-eye-slash", "active");
        toggle.classList.add("bi-eye");
      }
    });
  });
  
  passwordTogglesInitialized = true;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initPasswordToggles);
