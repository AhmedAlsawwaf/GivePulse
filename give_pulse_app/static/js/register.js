  document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll(".toggle-password");
    toggles.forEach(toggle => {
      const targetId = toggle.getAttribute("data-target");
      const input = document.getElementById(targetId);

      toggle.addEventListener("click", () => {
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
  });
