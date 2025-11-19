// Esperar a que el DOM cargue antes de ejecutar el código
document.addEventListener("DOMContentLoaded", function () {

  // Recibir datos desde Django
  const datosEscuelas = window.datosEscuelas || [];

  // === Funciones ===
  window.mostrarModulo = function (id) {
    document.querySelectorAll('.modulo-escuela').forEach(mod => mod.classList.add('oculto'));
    document.getElementById(id).classList.remove('oculto');
  };

  window.cerrarModulo = function () {
    document.querySelectorAll('.modulo-escuela').forEach(mod => mod.classList.add('oculto'));
  };

  // 🔹 Mostrar/Ocultar sección de gráficos (sin generarlos aquí)
  window.mostrarGraficos = function () {
    const seccion = document.getElementById("graficos");
    if (seccion) {
      seccion.classList.toggle("oculto");
    } else {
      console.warn("⚠️ No se encontró la sección de gráficos.");
    }
  };

});
