document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll("table tbody tr");
  const donors = [];

  rows.forEach(row => {
    const cells = row.querySelectorAll("td");
    const name = cells[1].textContent.trim();
    const count = parseInt(cells[2].textContent.trim(), 10);

    const existing = donors.find(d => d.name === name);
    if (existing) {
      existing.count += count;
    } else {
      donors.push({ name, count });
    }
  });

  donors.sort((a, b) => b.count - a.count);
  const topDonors = donors.slice(0, 10);

  const names = topDonors.map(d => d.name);
  const counts = topDonors.map(d => d.count);

  const ctx = document.getElementById("donationsChart").getContext("2d");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "Number of Donations",
        data: counts,
        backgroundColor: [
          "#ED3744", 
          "#A5B68E", 
          "#ED3744CC", 
          "#A5B68ECC", 
          "#F5F5F5",   
          "#ED374480",
          "#A5B68E99",
          "#ED3744B3",
          "#A5B68EB3",
          "#ED374466"
        ],
        borderColor: "#212121",
        borderWidth: 1.5,
        borderRadius: 8,
        hoverBackgroundColor: "#ED3744B3"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: "Top 10 Donors",
          color: "#212121",
          font: { size: 22, weight: 'bold' },
          padding: { bottom: 20 }
        },
        tooltip: {
          backgroundColor: "#212121",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "#A5B68E",
          borderWidth: 1
        }
      },
      layout: { padding: { top: 20, bottom: 20 } },
      scales: {
        x: {
          title: {
            display: true,
            text: "Donors",
            color: "#212121",
            font: { size: 16, weight: 'bold' }
          },
          ticks: {
            color: "#212121"
          },
          grid: {
            display: false
          }
        },
        y: {
          title: {
            display: true,
            text: "Number of Donations",
            color: "#212121",
            font: { size: 16, weight: 'bold' }
          },
          ticks: {
            color: "#212121",
            stepSize: 1
          },
          grid: {
            color: "#F5F5F5"
          },
          beginAtZero: true
        }
      },
      animation: {
        duration: 1500,
        easing: "easeOutBounce"
      }
    },
  });
});
