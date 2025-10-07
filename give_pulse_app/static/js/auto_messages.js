
document.addEventListener("DOMContentLoaded", () => {
  const messages = document.querySelectorAll(".alert");
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 500);
    }, 5000);
  });
});
