// Mostrar módulo
function mostrarModulo(id) {
  document.querySelectorAll('.modulo-escuela').forEach(m => m.classList.add('oculto'));
  document.getElementById(id).classList.remove('oculto');
  crearGraficos();
}

// Cerrar módulo
function cerrarModulo() {
  document.querySelectorAll('.modulo-escuela').forEach(m => m.classList.add('oculto'));
}

// Mostrar/Ocultar gráficos
function mostrarGraficos() {
  const g = document.getElementById('graficos');
  g.classList.toggle('oculto');
}

// Editar módulo (placeholder)
function editarModulo() {
  alert("Función de edición en desarrollo.");
}

// Crear gráficos Chart.js
function crearGraficos() {
  const emocionesCtx = document.getElementById('chartEmociones');
  const seccionesCtx = document.getElementById('chartSecciones');
  const comparativaCtx = document.getElementById('chartComparativa');

  if (!emocionesCtx || emocionesCtx.dataset.loaded) return;
  emocionesCtx.dataset.loaded = true;

  new Chart(emocionesCtx, {
    type: 'bar',
    data: {
      labels: ['Alegría', 'Tristeza', 'Ira', 'Sorpresa', 'Miedo'],
      datasets: [{
        label: 'Nivel Emocional',
        data: [12, 5, 8, 4, 3],
        backgroundColor: ['#42a5f5','#ef5350','#66bb6a','#ffa726','#ab47bc']
      }]
    }
  });

  new Chart(seccionesCtx, {
    type: 'doughnut',
    data: {
      labels: ['A', 'B', 'C', 'D'],
      datasets: [{
        label: 'Cantidad de Secciones',
        data: [3, 4, 2, 1],
        backgroundColor: ['#5c6bc0','#29b6f6','#8bc34a','#ff7043']
      }]
    }
  });

  new Chart(comparativaCtx, {
    type: 'line',
    data: {
      labels: ['1°', '2°', '3°', '4° Medio'],
      datasets: [{
        label: 'Comparativa General',
        data: [10, 15, 13, 18],
        borderColor: '#3949ab',
        fill: false
      }]
    }
  });
}

// Generar PDF con los gráficos incluidos
async function descargarPDF(nombreEscuela) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

  doc.setFontSize(18);
  doc.text(`Informe Psicológico — ${nombreEscuela}`, 10, 20);
  doc.setFontSize(12);
  doc.text(`Psicóloga: {{ user.first_name }} {{ user.last_name }}`, 10, 30);
  doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 10, 38);

  doc.setFontSize(14);
  doc.text("Resumen General:", 10, 50);
  doc.setFontSize(11);
  doc.text([
    "- Perfil Psicosocial del Grupo",
    "- Clima Escolar y de Aula",
    "- Factores de Riesgo y Protección",
    "- Fortalezas del Grupo",
    "- Necesidades de Intervención"
  ], 15, 58);

  // Capturar los gráficos como imágenes
  const charts = ['chartEmociones', 'chartSecciones', 'chartComparativa'];
  let yPos = 110;

  for (let id of charts) {
    const canvas = document.getElementById(id);
    const imgData = await html2canvas(canvas).then(c => c.toDataURL('image/png'));
    doc.addImage(imgData, 'PNG', 10, yPos, 90, 60);
    if (id !== 'chartComparativa') yPos += 65;
  }

  // Página adicional con espacio para observaciones
  doc.addPage();
  doc.setFontSize(16);
  doc.text("🧠 Observaciones de la Psicóloga", 10, 20);
  doc.setFontSize(12);
  doc.text("Notas:", 10, 30);
  doc.rect(10, 35, 190, 230); // espacio para escribir

  doc.save(`informe_${nombreEscuela}.pdf`);
}
