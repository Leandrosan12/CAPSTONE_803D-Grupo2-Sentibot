document.addEventListener("DOMContentLoaded", () => {
    // Gráfico de barras global
    const ctxBarras = document.getElementById('chartBarras').getContext('2d');
    new Chart(ctxBarras, {
        type: 'bar',
        data: {
            labels: emocionesData.map(e => e.nombre_emocion),
            datasets: [{
                label: 'Cantidad de emociones',
                data: emocionesData.map(e => e.cantidad),
                backgroundColor: ['#4caf50','#f44336','#ffeb3b','#2196f3','#9c27b0','#607d8b']
            }]
        }
    });

    // Gráfico de pastel global
    const ctxPastel = document.getElementById('chartPastel').getContext('2d');
    new Chart(ctxPastel, {
        type: 'pie',
        data: {
            labels: emocionesData.map(e => e.nombre_emocion),
            datasets: [{
                data: emocionesData.map(e => e.cantidad),
                backgroundColor: ['#4caf50','#f44336','#ffeb3b','#2196f3','#9c27b0','#607d8b']
            }]
        }
    });

    // Gráfico radar de primer usuario (puedes iterar luego)
    if(datosUsuarios.length > 0){
        const ctxRadar = document.getElementById('chartRadar').getContext('2d');
        const radarData = {
            labels: datosUsuarios[0].emociones.map(e => e.nombre_emocion),
            datasets: [{
                label: datosUsuarios[0].usuario,
                data: datosUsuarios[0].emociones.map(e => e.cantidad),
                fill: true,
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)"
            }]
        };
        new Chart(ctxRadar, { type: 'radar', data: radarData });
    }
});
