document.addEventListener("DOMContentLoaded", () => {
  // --- 🧩 Validación general ---
  if (typeof Chart === "undefined") {
    console.error("⚠️ Chart.js no está cargado correctamente.");
    return;
  }

  // === 🟢 Gráfico Global de Emociones ===
  if (emocionesGlobales && Object.keys(emocionesGlobales).length > 0) {
    const ctxGlobal = document.getElementById("graficoGlobal");
    if (ctxGlobal) {
      new Chart(ctxGlobal, {
        type: "pie",
        data: {
          labels: ["Feliz", "Triste", "Neutral", "Enojado", "Sorprendido", "Sin reconocer"],
          datasets: [{
            data: Object.values(emocionesGlobales),
            backgroundColor: [
              "#4CAF50", "#5B73E8", "#FFC107", "#E53935", "#9C27B0", "#9E9E9E"
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom" } }
        }
      });
    }
  }

  // === 🔵 Duración promedio por escuela ===
  if (Array.isArray(datosDuracion) && datosDuracion.length > 0) {
    const ctxDuracion = document.getElementById("graficoDuracion");
    if (ctxDuracion) {
      new Chart(ctxDuracion, {
        type: "bar",
        data: {
          labels: datosDuracion.map(e => e.escuela),
          datasets: [{
            label: "Duración promedio (seg)",
            data: datosDuracion.map(e => e.promedio),
            backgroundColor: "#5B73E8"
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } },
          plugins: { legend: { display: false } }
        }
      });
    }
  }

  // === 🟣 Satisfacción general ===
  if (Array.isArray(datosSatisfaccion) && datosSatisfaccion.length > 0) {
    const ctxSatisfaccion = document.getElementById("graficoSatisfaccion");
    if (ctxSatisfaccion) {
      new Chart(ctxSatisfaccion, {
        type: "bar",
        data: {
          labels: datosSatisfaccion.map(e => e.escuela),
          datasets: [
            {
              label: "Sí le gustó",
              data: datosSatisfaccion.map(e => e.si),
              backgroundColor: "#4CAF50"
            },
            {
              label: "No le gustó",
              data: datosSatisfaccion.map(e => e.no),
              backgroundColor: "#E53935"
            }
          ]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } },
          plugins: { legend: { position: "bottom" } }
        }
      });
    }
  }

  // === 🟠 Gráficos individuales por escuela ===
  const contenedor = document.getElementById("contenedorEscuelas");
  if (Array.isArray(datosEscuelas) && datosEscuelas.length > 0 && contenedor) {
    datosEscuelas.forEach((escuela, index) => {
      const card = document.createElement("div");
      card.classList.add("card", "p-3", "m-2", "shadow-sm", "bg-dark", "text-white");
      card.style.flex = "1 1 300px";
      card.innerHTML = `
        <h5 class="text-center mb-3">${escuela.escuela}</h5>
        <canvas id="graficoEscuela${index}"></canvas>
      `;
      contenedor.appendChild(card);

      const ctxEscuela = document.getElementById(`graficoEscuela${index}`);
      if (ctxEscuela) {
        new Chart(ctxEscuela, {
          type: "pie",
          data: {
            labels: ["Feliz", "Triste", "Neutral", "Enojado", "Sorprendido", "Sin reconocer"],
            datasets: [{
              data: Object.values(escuela.emociones),
              backgroundColor: [
                "#4CAF50", "#5B73E8", "#FFC107", "#E53935", "#9C27B0", "#9E9E9E"
              ]
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { position: "bottom" } }
          }
        });
      }
    });
  }

  // === 🧾 Descargar todos los gráficos como PDF ===
  window.descargarGraficosPDF = async () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF("p", "mm", "a4");
    const contenedor = document.getElementById("contenedorGraficos");

    await html2canvas(contenedor, { scale: 2 }).then(canvas => {
      const imgData = canvas.toDataURL("image/png");
      const pageWidth = doc.internal.pageSize.getWidth();
      const imgHeight = (canvas.height * pageWidth) / canvas.width;
      doc.addImage(imgData, "PNG", 0, 0, pageWidth, imgHeight);
      doc.save("Dashboard_Profesor.pdf");
    });
  };
});
