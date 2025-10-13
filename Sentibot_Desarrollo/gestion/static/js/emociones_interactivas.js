let camaraActiva = false, stream = null;
let segundosFeliz = 0, segundosTriste = 0, segundosNeutral = 0, segundosNull = 0;

function activarCamara(si) {
    if (si) {
        document.getElementById('camaraSection').style.display = 'block';
        iniciarCamara();
    } else {
        window.location.href = window.location.origin + "/extra/";
    }
}

function iniciarCamara() {
    const videoCamara = document.getElementById('videoCamara');
    const estadoCamara = document.querySelector('.estado');
    const felizEl = document.getElementById('feliz');
    const tristeEl = document.getElementById('triste');
    const neutralEl = document.getElementById('neutral');
    const nullEl = document.getElementById('null');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            videoCamara.srcObject = stream;
            camaraActiva = true;
            estadoCamara.textContent = 'Cámara activa';

            tomarFoto();

            setInterval(() => {
                const emociones = ["Feliz", "Triste", "Neutral", "Null"];
                const emocion = emociones[Math.floor(Math.random() * emociones.length)];

                if (emocion === "Feliz") segundosFeliz += 5;
                if (emocion === "Triste") segundosTriste += 5;
                if (emocion === "Neutral") segundosNeutral += 5;
                if (emocion === "Null") segundosNull += 5;

                felizEl.textContent = `😊 Feliz: ${segundosFeliz} seg`;
                tristeEl.textContent = `😢 Triste: ${segundosTriste} seg`;
                neutralEl.textContent = `😐 Neutral: ${segundosNeutral} seg`;
                nullEl.textContent = `❓ Null: ${segundosNull} seg`;

                tomarFoto();
            }, 5000);
        })
        .catch(err => {
            estadoCamara.textContent = '⚠️ Error al iniciar cámara';
            console.error(err);
        });
}

function tomarFoto() {
    if (!camaraActiva) return;
    const videoCamara = document.getElementById('videoCamara');
    const capturedPhotoContainer = document.getElementById('capturedPhotoContainer');
    const canvas = document.createElement('canvas');
    canvas.width = videoCamara.videoWidth || 640;
    canvas.height = videoCamara.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoCamara, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL('image/png');
    capturedPhotoContainer.innerHTML = `
        <div class="captured-photo-card">
            <h6>📸 Foto capturada automáticamente</h6>
            <img src="${imgData}" alt="Foto captura">
        </div>
    `;
}
