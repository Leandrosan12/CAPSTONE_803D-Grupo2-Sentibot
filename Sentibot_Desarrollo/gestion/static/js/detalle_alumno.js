document.addEventListener("DOMContentLoaded", function () {

    // ============================
    //      EMOCIONES
    // ============================
    const emocionesDiv = document.getElementById("emocionesData");

    const feliz = parseInt(emocionesDiv.dataset.feliz) || 0;
    const triste = parseInt(emocionesDiv.dataset.triste) || 0;
    const neutral = parseInt(emocionesDiv.dataset.neutral) || 0;
    const enojado = parseInt(emocionesDiv.dataset.enojado) || 0;
    const sorprendido = parseInt(emocionesDiv.dataset.sorprendido) || 0;

    const ctx1 = document.getElementById("pieChartEmociones").getContext("2d");

    new Chart(ctx1, {
        type: "pie",
        data: {
            labels: ["Feliz", "Triste", "Neutral", "Enojado", "Sorprendido"],
            datasets: [{
                data: [feliz, triste, neutral, enojado, sorprendido]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });

    // ============================
    //      ENCUESTA
    // ============================
    const encuestaDiv = document.getElementById("encuestaData");
    const recomendacion = parseInt(encuestaDiv.dataset.recomendacion) || 0;

    const ctx2 = document.getElementById("barChartEncuesta").getContext("2d");

    new Chart(ctx2, {
        type: "bar",
        data: {
            labels: ["Recomendación"],
            datasets: [{
                label: "Puntaje (1-10)",
                data: [recomendacion]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 10 }
            }
        }
    });

});
