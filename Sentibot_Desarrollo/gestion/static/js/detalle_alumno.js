document.addEventListener("DOMContentLoaded", () => {
  const alumnoCard = document.getElementById("alumnoInfo");
  const btnEditar = document.getElementById("btnEditar");
  const btnHistorial = document.getElementById("btnHistorial");
  const btnCerrarHistorial = document.getElementById("btnCerrarHistorial");
  const historialContainer = document.getElementById("historialContainer");
  const resumenEmociones = document.getElementById("resumenEmociones");
  const listaActividades = document.getElementById("listaActividades");
  const btnDescargarPDF = document.getElementById("btnDescargarPDF");
  const canvas = document.getElementById("chartEmociones");

  if (!alumnoCard) {
    console.error("❌ No se encontró el contenedor del alumno (alumnoInfo).");
    return;
  }

  // Leer datos del alumno
  const alumnoId = alumnoCard.dataset.alumnoId;
  const nombre = alumnoCard.dataset.nombre;
  const sede = alumnoCard.dataset.escuela;
  const email = alumnoCard.dataset.email;
  const rut = alumnoCard.dataset.rut;
  const rol = alumnoCard.dataset.rol;

  // Datos simulados (reemplázalos si quieres con datos reales)
  const emociones = [
    { tipo: "Felicidad", porcentaje: 40 },
    { tipo: "Tristeza", porcentaje: 20 },
    { tipo: "Ira", porcentaje: 15 },
    { tipo: "Sorpresa", porcentaje: 10 },
    { tipo: "Neutral", porcentaje: 15 }
  ];

  const actividades = [
    "Participó en una dinámica grupal (Emoción: Felicidad)",
    "Entrevista de autoevaluación emocional (Emoción: Tristeza)",
    "Presentación oral (Emoción: Sorpresa)",
    "Trabajo colaborativo (Emoción: Neutral)"
  ];

  // Botón HISTORIAL
  btnHistorial.addEventListener("click", () => {
    historialContainer.style.display = "block";

    resumenEmociones.innerHTML = `
      <p class="lead">
        Registro de emociones detectadas mediante cámara y actividades asociadas.
      </p>
      <p><strong>Emoción predominante:</strong> ${emociones[0].tipo}</p>
    `;

    // Renderizar gráfico
    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: emociones.map(e => e.tipo),
        datasets: [{
          data: emociones.map(e => e.porcentaje),
          backgroundColor: ["#28a745", "#007bff", "#ffc107", "#dc3545", "#6c757d"]
        }]
      },
      options: {
        plugins: { legend: { position: "bottom" } },
        responsive: false
      }
    });

    // Listar actividades
    listaActividades.innerHTML = "";
    actividades.forEach(a => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.textContent = a;
      listaActividades.appendChild(li);
    });
  });

  // Botón CERRAR HISTORIAL
  btnCerrarHistorial.addEventListener("click", () => {
    historialContainer.style.display = "none";
  });

  // Botón EDITAR
  btnEditar.addEventListener("click", () => {
    if (alumnoId) {
      window.location.href = `/editar_alumno/${alumnoId}/`;
    } else {
      alert("No se pudo identificar el alumno.");
    }
  });

  // Botón DESCARGAR PDF
  btnDescargarPDF.addEventListener("click", async () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const fechaHora = new Date().toLocaleString();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text(sede, 20, 20);
    doc.setFontSize(14);
    doc.text("Informe de Emociones y Actividades", 20, 30);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.text("Generado: " + fechaHora, 20, 40);
    doc.text("Alumno: " + nombre, 20, 50);
    doc.text("Correo: " + email, 20, 60);
    doc.text("Rut: " + rut, 20, 70);
    doc.text("Rol: " + rol, 20, 80);
    doc.text("Emoción predominante: " + emociones[0].tipo, 20, 90);

    // Lista de actividades
    let y = 105;
    doc.text("Actividades:", 20, y);
    y += 10;
    actividades.forEach(a => {
      doc.text("- " + a, 25, y);
      y += 10;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save(`Informe_${nombre.replace(/\s+/g, "_")}.pdf`);
  });
});
