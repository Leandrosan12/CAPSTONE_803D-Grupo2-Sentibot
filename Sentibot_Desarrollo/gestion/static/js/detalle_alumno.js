document.addEventListener("DOMContentLoaded", function () {
    // -----------------------------
    // Elementos del DOM
    // -----------------------------
    const alumnoCard = document.getElementById("alumnoInfo");
    const editarForm = document.getElementById("editarForm");

    const btnEditar = document.getElementById("btnEditar");
    const btnGuardar = document.getElementById("btnGuardar");
    const btnCancelar = document.getElementById("btnCancelar");

    const id = alumnoCard.dataset.id;

    const editNombre = document.getElementById("editNombre");
    const editApellido = document.getElementById("editApellido");
    const editEmail = document.getElementById("editEmail");
    const editEscuela = document.getElementById("editEscuela");
    const editRol = document.getElementById("editRol");

    // -----------------------------
    // Función para setear select
    // -----------------------------
    function setSelectValue(selectElement, value) {
        if (!value) return;
        for (const opt of selectElement.options) {
            if (String(opt.value) === String(value)) {
                opt.selected = true;
                break;
            }
        }
    }

    // -----------------------------
    // Abrir formulario de edición
    // -----------------------------
    btnEditar.addEventListener("click", () => {
        editNombre.value = alumnoCard.dataset.nombre;
        editApellido.value = alumnoCard.dataset.apellido;
        editEmail.value = alumnoCard.dataset.email;
        setSelectValue(editEscuela, alumnoCard.dataset.escuela);
        setSelectValue(editRol, alumnoCard.dataset.rol);
            Form.style.display = "block";
    });

    // -----------------------------
    // Cancelar edición
    // -----------------------------
    btnCancelar.addEventListener("click", () => {
        editarForm.style.display = "none";
    });

    // -----------------------------
    // Guardar cambios vía POST
    // -----------------------------
    btnGuardar.addEventListener("click", async () => {
        const datos = {
            nombre: editNombre.value,
            apellido: editApellido.value,
            email: editEmail.value,
            escuela: editEscuela.value,
            rol: editRol.value
        };

        try {
            const response = await fetch(`/actualizar_alumno/${id}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(datos)
            });

            if (response.ok) {
                alert("Alumno actualizado correctamente.");
                location.reload();
            } else {
                const errorData = await response.json();
                alert("Error al actualizar el alumno: " + (errorData.error || "Error desconocido"));
            }
        } catch (err) {
            alert("Error en la petición: " + err);
        }
    });

    // -----------------------------
    // Función para obtener cookie CSRF
    // -----------------------------
    function getCookie(name) {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    // ==========================
    // Gráfico Pie - Emociones
    // ==========================
    const emo = document.getElementById("emocionesData").dataset;
    new Chart(document.getElementById("pieChartEmociones"), {
        type: "pie",
        data: {
            labels: ["Feliz", "Triste", "Neutral", "Enojado", "Sorprendido"],
            datasets: [{
                data: [
                    parseInt(emo.feliz) || 0,
                    parseInt(emo.triste) || 0,
                    parseInt(emo.neutral) || 0,
                    parseInt(emo.enojado) || 0,
                    parseInt(emo.sorprendido) || 0
                ],
                backgroundColor: ['#FFD700','#1E90FF','#A9A9A9','#FF4500','#FF69B4']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // ==========================
    // Gráfico Barras - Encuesta
    // ==========================
    const encuesta = document.getElementById("encuestaData").dataset;
    new Chart(document.getElementById("barChartEncuesta"), {
        type: "bar",
        data: {
            labels: ["Recomendación"],
            datasets: [{
                label: "Puntaje",
                data: [parseInt(encuesta.recomendacion) || 0],
                backgroundColor: ['#4CAF50']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, max: 10 } }
        }
    });
});
