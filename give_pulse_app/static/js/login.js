  document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("id_password");
    const icon = togglePassword.querySelector("i");

    togglePassword.addEventListener("click", function () {
      const type = passwordInput.type === "password" ? "text" : "password";
      passwordInput.type = type;
      icon.classList.toggle("bi-eye");
      icon.classList.toggle("bi-eye-slash");

      icon.style.color = passwordInput.type === "text" ? "var(--primary-red)" : "#aaa";
    });
  });