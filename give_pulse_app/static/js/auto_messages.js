
document.addEventListener("DOMContentLoaded", () => {
  const messages = document.querySelectorAll(".fade-message");
  messages.forEach(msg => {
    setTimeout(() => {
      msg.classList.add("fade-out");
      setTimeout(() => msg.remove(), 600);
    }, 3000);
  });
});
