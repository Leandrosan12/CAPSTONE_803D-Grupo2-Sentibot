document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "https://apisentibot-production.up.railway.app/predict_emotion"; // 🌐 API externa
    const startBtn = document.getElementById('startBtn');
    const videoCamara = document.getElementById('videoCamara');
    const estadoCamara = document.querySelector('.estado');
    const fotoCapturada = document.getElementById('fotoCapturada');
    const emocionEnCamara = document.getElementById('emocionEnCamara');

    const felizEl = document.getElementById('feliz');
    const tristeEl = document.getElementById('triste');
    const neutralEl = document.getElementById('neutral');
    const enojadoEl = document.getElementById('enojado');
    const sorprendidoEl = document.getElementById('sorprendido');
    const sinreconocerEl = document.getElementById('sinreconocer');

    const estadoEl = document.getElementById('estado');
    const porcentajeEl = document.getElementById('porcentaje');
    const rostroEl = document.getElementById('rostro');
    const sujetoEl = document.getElementById('sujeto');

    let stream = null;
    let camaraEncendida = false;
    let segundos = { Feliz: 0, Triste: 0, Neutral: 0, Enojado: 0, Sorprendido: 0, SinReconocer: 0 };

    startBtn.addEventListener('click', async () => {
        if (!camaraEncendida) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                videoCamara.srcObject = stream;
                estadoCamara.textContent = 'Cámara activa';
                camaraEncendida = true;
                startBtn.textContent = 'Apagar Cámara';

                const intervalo = setInterval(() => {
                    if (camaraEncendida) capturarYPredecir();
                    else clearInterval(intervalo);
                }, 2000);

            } catch (err) {
                console.error(err);
                estadoCamara.textContent = 'Error al iniciar cámara';
            }
        } else {
            stream.getTracks().forEach(track => track.stop());
            videoCamara.srcObject = null;
            estadoCamara.textContent = 'Apagado';
            camaraEncendida = false;
            startBtn.textContent = 'Iniciar Cámara';
        }
    });

    function capturarYPredecir() {
        const canvas = document.createElement('canvas');
        const size = 220;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        const vw = videoCamara.videoWidth;
        const vh = videoCamara.videoHeight;
        const sx = (vw - size) / 2;
        const sy = (vh - size) / 2;
        ctx.drawImage(videoCamara, sx, sy, size, size, 0, 0, size, size);

        const fotoBase64 = canvas.toDataURL('image/png');
        fotoCapturada.src = fotoBase64;

        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: fotoBase64 })
        })
        .then(res => res.json())
        .then(data => {
            let emocion = data.label || "Sin reconocer";
            const confianza = data.confidence || 0;

            if (!['Feliz','Triste','Neutral','Enojado','Sorprendido'].includes(emocion)) {
                emocion = "SinReconocer";
            }

            emocionEnCamara.textContent = `${emocion} — ${confianza.toFixed(1)}%`;
            estadoEl.textContent = `Estado: ${emocion}`;
            porcentajeEl.textContent = `Porcentaje: ${confianza.toFixed(2)}%`;
            rostroEl.textContent = `Estado del rostro: Detectado`;
            sujetoEl.textContent = `Id: 001`;

            segundos[emocion] += 2;

            felizEl.textContent = `Feliz: ${segundos.Feliz} seg`;
            tristeEl.textContent = `Triste: ${segundos.Triste} seg`;
            neutralEl.textContent = `Neutral: ${segundos.Neutral} seg`;
            enojadoEl.textContent = `Enojado: ${segundos.Enojado} seg`;
            sorprendidoEl.textContent = `Sorprendido: ${segundos.Sorprendido} seg`;
            sinreconocerEl.textContent = `Sin reconocer: ${segundos.SinReconocer} seg`;
        })
        .catch(err => console.error("Error predicción:", err));
    }
});
