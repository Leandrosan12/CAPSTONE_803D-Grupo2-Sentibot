document.addEventListener("DOMContentLoaded", () => {
    // 🔹 URL de la API LOCAL (FastAPI)
    const API_URL = "http://127.0.0.1:8001/predict/";

    // 🔹 URL de tu backend Django
    const BACKEND_URL = "http://127.0.0.1:8000/emocion_camara/registrar_emocion/";

    const startBtn = document.getElementById('startBtn');
    const videoCamara = document.getElementById('videoCamara');
    const estadoCamara = document.querySelector('.estado');
    const fotoCapturada = document.getElementById('fotoCapturada');
    const emocionEnCamara = document.getElementById('emocionEnCamara');

    const felizEl = document.getElementById('feliz');
    const tristeEl = document.getElementById('triste');
    const neutralEl = document.getElementById('neutral');
    const enojadoEl = document.getElementById('enojado');
    const sinreconocerEl = document.getElementById('sinreconocer');

    const estadoEl = document.getElementById('estado');
    const porcentajeEl = document.getElementById('porcentaje');
    const rostroEl = document.getElementById('rostro');
    const sujetoEl = document.getElementById('sujeto');

    // 🔴🟢 Indicador de estado de la API
    const apiStatusCircle = document.createElement('div');
    apiStatusCircle.classList.add('circle');
    const apiStatusText = document.createElement('span');
    apiStatusText.classList.add('status-text');
    apiStatusText.textContent = "API";

    const apiStatusDiv = document.createElement('div');
    apiStatusDiv.classList.add('api-status', 'offline'); // inicial offline
    apiStatusDiv.appendChild(apiStatusCircle);
    apiStatusDiv.appendChild(apiStatusText);

    // Insertamos el indicador arriba del video
    const camaraContainer = document.querySelector('.camara-container');
    camaraContainer.parentNode.insertBefore(apiStatusDiv, camaraContainer);

    const csrftokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrftoken = csrftokenMeta ? csrftokenMeta.content : "";

    let stream = null;
    let camaraEncendida = false;

    let segundos = { 
        Feliz: 0, 
        Triste: 0, 
        Neutral: 0, 
        Enojado: 0, 
        SinReconocer: 0 
    };

    const usuarioDiv = document.getElementById('usuario');
    const SESION_ID = usuarioDiv ? usuarioDiv.dataset.sesion : null;

    if (!SESION_ID) {
        console.error("SESION_ID no definido. No se guardarán emociones.");
    }

function verificarAPI() {
    // Ping a la API con GET rápido (o POST con body vacío si GET no existe)
    fetch(API_URL, { method: 'GET', cache: 'no-store' })
        .then(res => {
            if (res.ok) {
                apiStatusDiv.classList.remove('offline');
                apiStatusDiv.classList.add('online');
            } else {
                apiStatusDiv.classList.remove('online');
                apiStatusDiv.classList.add('offline');
            }
        })
        .catch(() => {
            apiStatusDiv.classList.remove('online');
            apiStatusDiv.classList.add('offline');
        });
}


    // verificar API cada 5s
    verificarAPI();
    setInterval(verificarAPI, 5000);

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
            if (stream) stream.getTracks().forEach(track => track.stop());
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

        const blob = dataURLtoBlob(fotoBase64);
        const formData = new FormData();
        formData.append("file", blob, "frame.png");

        fetch(API_URL, {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            let emocion = (data.emotion || data.dominant_emotion || "SinReconocer");
            let confianza = (data.confidence || data.score || 0);
            if (confianza > 1) confianza = confianza / 100;
            confianza = Math.min(Math.max(confianza, 0), 1);
            const confianzaPorcentaje = (confianza * 100).toFixed(2);

            if (!['Feliz','Triste','Neutral','Enojado'].includes(emocion)) {
                emocion = "SinReconocer";
            }

            emocionEnCamara.textContent = `${emocion} — ${confianzaPorcentaje}%`;
            estadoEl.textContent = `Estado: ${emocion}`;
            porcentajeEl.textContent = `Porcentaje: ${confianzaPorcentaje}%`;
            rostroEl.textContent = `Estado del rostro: Detectado`;
            sujetoEl.textContent = `Id: 001`;

            segundos[emocion] += 2;
            felizEl.textContent = `Feliz: ${segundos.Feliz} seg`;
            tristeEl.textContent = `Triste: ${segundos.Triste} seg`;
            neutralEl.textContent = `Neutral: ${segundos.Neutral} seg`;
            enojadoEl.textContent = `Enojado: ${segundos.Enojado} seg`;
            sinreconocerEl.textContent = `Sin reconocer: ${segundos.SinReconocer} seg`;

            if (csrftoken && SESION_ID) {
                fetch(BACKEND_URL, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({
                        sesion_id: SESION_ID,
                        nombre_emocion: emocion,
                        probabilidad: confianzaPorcentaje,
                        duracion: 2,
                        fiabilidad: confianza
                    })
                })
                .then(res => res.json())
                .then(resp => console.log("✅ Emoción guardada:", resp))
                .catch(err => console.error("Error al guardar emoción:", err));
            }
        })  
        .catch(err => console.error("❌ Error predicción:", err));
    }

    function dataURLtoBlob(dataURL) {
        const byteString = atob(dataURL.split(',')[1]);
        const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) ia[i] = byteString.charCodeAt(i);
        return new Blob([ab], { type: mimeString });
    }
});
