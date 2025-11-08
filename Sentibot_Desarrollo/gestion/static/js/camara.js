document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById('startBtn');
  const videoCamara = document.getElementById('videoCamara');
  const estadoCamara = document.querySelector('.estado');
  const fotoCapturada = document.getElementById('fotoCapturada');

  const felizEl = document.getElementById('feliz');
  const tristeEl = document.getElementById('triste');
  const neutralEl = document.getElementById('neutral');
  const nullEl = document.getElementById('null');

  const estadoEl = document.getElementById('estado');
  const porcentajeEl = document.getElementById('porcentaje');
  const rostroEl = document.getElementById('rostro');
  const sujetoEl = document.getElementById('sujeto');

  let stream = null;
  let fotoInterval = null;
  let camaraEncendida = false;

  let segundosFeliz = 0, segundosTriste = 0, segundosNeutral = 0, segundosNull = 0;

  startBtn.addEventListener('click', async () => {
    if (!camaraEncendida) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        videoCamara.srcObject = stream;
        estadoCamara.textContent = 'Cámara activa';
        camaraEncendida = true;
        startBtn.textContent = 'Apagar';

        fotoInterval = setInterval(() => {
          const canvas = document.createElement('canvas');
          canvas.width = videoCamara.videoWidth;
          canvas.height = videoCamara.videoHeight;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(videoCamara, 0, 0, canvas.width, canvas.height);
          const fotoBase64 = canvas.toDataURL('image/png');
          fotoCapturada.src = fotoBase64;

          const emociones = ["Feliz", "Triste", "Neutral", "Null"];
          const emocionRandom = emociones[Math.floor(Math.random() * emociones.length)];
          const porcentajeRandom = Math.floor(Math.random() * 100) + 1;

          if (emocionRandom === "Feliz") segundosFeliz += 10;
          if (emocionRandom === "Triste") segundosTriste += 10;
          if (emocionRandom === "Neutral") segundosNeutral += 10;
          if (emocionRandom === "Null") segundosNull += 10;

          felizEl.textContent = `Feliz: ${segundosFeliz} seg`;
          tristeEl.textContent = `Triste: ${segundosTriste} seg`;
          neutralEl.textContent = `Neutral: ${segundosNeutral} seg`;
          nullEl.textContent = `Null: ${segundosNull} seg`;

          estadoEl.textContent = `Estado: ${emocionRandom}`;
          porcentajeEl.textContent = `Porcentaje: ${porcentajeRandom}%`;
          rostroEl.textContent = `Estado del rostro: Detectado`;
          sujetoEl.textContent = `Id: 001`;
        }, 5000);

      } catch (err) {
        console.error("Error al acceder a la cámara: ", err);
        estadoCamara.textContent = 'Error al iniciar cámara';
      }
    } else {
      stream.getTracks().forEach(track => track.stop());
      videoCamara.srcObject = null;
      clearInterval(fotoInterval);
      estadoCamara.textContent = 'Apagado';
      camaraEncendida = false;
      startBtn.textContent = 'Iniciar';
    }
  });
});
