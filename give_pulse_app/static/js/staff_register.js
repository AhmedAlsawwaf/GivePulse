document.addEventListener("DOMContentLoaded", function () {

  // 👁 Password toggle logic
  const toggles = document.querySelectorAll(".toggle-password");
  toggles.forEach(toggle => {
    const targetId = toggle.getAttribute("data-target");
    const input = document.getElementById(targetId);

    if (!input) {
      console.warn(`⚠️ Input not found for: ${targetId}`);
      return;
    }

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

  // 🏥 City → Hospital dynamic loading
  const citySelect = document.getElementById("id_city");
  const hospitalSelect = document.getElementById("id_hospital");
  const loading = document.getElementById("hospitals-loading");
  const emptyMsg = document.getElementById("hospitals-empty");

  function clearHospitals() {
    hospitalSelect.innerHTML = "";
    hospitalSelect.disabled = true;
    emptyMsg.style.display = "none";
  }

  function populateHospitals(items) {
    hospitalSelect.innerHTML = "";
    if (!items || !items.length) {
      hospitalSelect.disabled = true;
      emptyMsg.style.display = "block";
      return;
    }

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a hospital";
    hospitalSelect.appendChild(placeholder);

    items.forEach(item => {
      const opt = document.createElement("option");
      opt.value = item.id;
      opt.textContent = item.name;
      hospitalSelect.appendChild(opt);
    });

    hospitalSelect.disabled = false;
    emptyMsg.style.display = "none";
  }

  async function fetchHospitals(cityId) {
    if (!cityId) {
      clearHospitals();
      return;
    }

    loading.style.display = "block";
    clearHospitals();

    try {
      const res = await fetch(`/hospitals/?city_id=${encodeURIComponent(cityId)}`, {
        headers: { "Accept": "application/json" }
      });
      const data = await res.json();
      populateHospitals(data.results || []);
    } catch (e) {
      console.error("Error fetching hospitals:", e);
      clearHospitals();
    } finally {
      loading.style.display = "none";
    }
  }

  if (citySelect) {
    citySelect.addEventListener("change", function () {
      fetchHospitals(this.value);
    });

    if (citySelect.value) {
      fetchHospitals(citySelect.value).then(() => {
        const prev = hospitalSelect.getAttribute("data-prev");
        if (prev) hospitalSelect.value = prev;
      });
    } else {
      clearHospitals();
    }
  }
});
