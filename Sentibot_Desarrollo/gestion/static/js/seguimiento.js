document.addEventListener("DOMContentLoaded", function() {
  const colors = ['#6a11cb', '#2575fc', '#ff7eb3', '#fbc531', '#4cd137'];

  // Gráfico de Barras
  new Chart(document.getElementById('chartBarras'), {
    type: 'bar',
    data: {
      labels: ['Alegría', 'Tristeza', 'Ira', 'Miedo', 'Asco'],
      datasets: [{
        label: 'Frecuencia',
        data: [12, 19, 17, 5, 8],
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });

  // Gráfico de Pastel
  new Chart(document.getElementById('chartPastel'), {
    type: 'pie',
    data: {
      labels: ['Alegría', 'Tristeza', 'Ira', 'Miedo', 'Asco'],
      datasets: [{
        data: [10, 20, 15, 8, 7],
        backgroundColor: colors
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // Gráfico tipo Gauge
  new Chart(document.getElementById('chartGauge'), {
    type: 'doughnut',
    data: {
      labels: ['Progreso', 'Restante'],
      datasets: [{
        data: [75, 25],
        backgroundColor: ['#6a11cb', '#e0e0e0'],
        cutout: '70%'
      }]
    },
    options: {
      rotation: -90,
      circumference: 180,
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });

  // Gráfico Radar
  new Chart(document.getElementById('chartRadar'), {
    type: 'radar',
    data: {
      labels: ['Alegría', 'Tristeza', 'Ira', 'Miedo', 'Asco'],
      datasets: [{
        label: 'Intensidad',
        data: [15, 20, 10, 8, 12],
        backgroundColor: 'rgba(106, 17, 203, 0.2)',
        borderColor: '#6a11cb',
        pointBackgroundColor: '#2575fc'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          grid: { color: '#ccc' },
          angleLines: { color: '#ddd' }
        }
      }
    }
  });
});
