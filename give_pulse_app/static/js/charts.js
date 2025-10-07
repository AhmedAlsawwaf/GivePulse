
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
            "rgba(255, 99, 132, 0.7)",
            "rgba(54, 162, 235, 0.7)",
            "rgba(255, 206, 86, 0.7)",
            "rgba(75, 192, 192, 0.7)",
            "rgba(153, 102, 255, 0.7)",
            "rgba(255, 159, 64, 0.7)",
            "rgba(199, 199, 199, 0.7)",
            "rgba(255, 99, 132, 0.7)",
            "rgba(54, 162, 235, 0.7)",
            "rgba(255, 206, 86, 0.7)"
          ],
          borderColor: "rgba(0,0,0,0.2)",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: "Top 10 Donors",
            font: { size: 20, weight: 'bold' },
            padding: { bottom: 20 }
          },
          
        },
        layout: {
          padding: { top: 20, bottom: 20 }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Donors", 
              font: { size: 16, weight: 'bold' }
            }
          },
          y: {
            title: {
              display: true,
              text: "Number of Donations",
              font: { size: 16, weight: 'bold' }
            },
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        }
      },
    });
  });
