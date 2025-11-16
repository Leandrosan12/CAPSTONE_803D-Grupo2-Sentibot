// preguntas.js

// Preguntas iniciales para definir emoción predominante
const preguntasIniciales = [
  {
    texto: "¿Cómo ha sido tu estado de ánimo la mayor parte del día?",
    opciones: [
      { letra: "A", texto: "Alegre o motivado", emocion: "Felicidad" },
      { letra: "B", texto: "Triste o desanimado", emocion: "Tristeza" },
      { letra: "C", texto: "Inquieto o asustado", emocion: "Miedo" },
      { letra: "D", texto: "Irritado o frustrado", emocion: "Enojo" }
    ]
  },
  {
    texto: "¿Qué describe mejor tu reacción ante lo que te ha pasado hoy?",
    opciones: [
      { letra: "A", texto: "Tengo ganas de compartir o celebrar", emocion: "Felicidad" },
      { letra: "B", texto: "Quisiera estar solo o descansar", emocion: "Tristeza" },
      { letra: "C", texto: "Me preocupa lo que pueda pasar", emocion: "Miedo" },
      { letra: "D", texto: "Siento que algo me molestó o me pareció injusto", emocion: "Enojo" }
    ]
  },
  {
    texto: "¿Cómo se siente tu cuerpo en este momento?",
    opciones: [
      { letra: "A", texto: "Liviano o con energía", emocion: "Felicidad" },
      { letra: "B", texto: "Pesado o sin fuerzas", emocion: "Tristeza" },
      { letra: "C", texto: "Tenso o con nervios", emocion: "Miedo" },
      { letra: "D", texto: "Caliente o con presión interna", emocion: "Enojo" }
    ]
  },
  {
    texto: "¿Qué necesitas más ahora?",
    opciones: [
      { letra: "A", texto: "Compartir algo positivo", emocion: "Felicidad" },
      { letra: "B", texto: "Apoyo o consuelo", emocion: "Tristeza" },
      { letra: "C", texto: "Sentirme seguro", emocion: "Miedo" },
      { letra: "D", texto: "Liberar tensión o desahogarme", emocion: "Enojo" }
    ]
  },
  {
    texto: "¿Qué palabra se acerca más a cómo te sientes?",
    opciones: [
      { letra: "A", texto: "Felicidad", emocion: "Felicidad" },
      { letra: "B", texto: "Tristeza", emocion: "Tristeza" },
      { letra: "C", texto: "Miedo", emocion: "Miedo" },
      { letra: "D", texto: "Enojo", emocion: "Enojo" }
    ]
  }
];

// Preguntas Sí/No según emoción ganadora
const preguntasSiNo = {
  Felicidad: [
    "¿Te sientes motivado/a para realizar tus actividades diarias?",
    "¿Disfrutas compartir momentos con otras personas?",
    "¿Te resulta fácil encontrar algo positivo en situaciones difíciles?",
    "¿Sueles dedicar tiempo a tus hobbies o pasatiempos favoritos?",
    "¿Te sientes satisfecho/a con los logros recientes que has tenido?"
  ],
  Tristeza: [
    "¿Te sientes desanimado/a con frecuencia?",
    "¿Tienes dificultad para encontrar motivación en tus actividades diarias?",
    "¿Te cuesta disfrutar de las cosas que antes te hacían feliz?",
    "¿Prefieres estar solo/a en lugar de compartir con otros?",
    "¿Has sentido cansancio o falta de energía la mayor parte del tiempo?"
  ],
  Miedo: [
    "¿Sientes inquietud o tensión ante situaciones nuevas?",
    "¿Evitas ciertas actividades por miedo a fracasar?",
    "¿Te preocupa con frecuencia lo que puede salir mal?",
    "¿Te cuesta tomar decisiones rápidamente por temor a equivocarte?",
    "¿Sientes tensión física (nudos, palpitaciones) en situaciones de estrés?"
  ],
  Enojo: [
    "¿Sueles irritarte fácilmente ante situaciones cotidianas?",
    "¿Te cuesta controlar tu temperamento en discusiones o conflictos?",
    "¿Sientes frustración cuando las cosas no salen como planeaste?",
    "¿Tiendes a culpar a otros por problemas que te afectan?",
    "¿Experimentas tensión física (mandíbula apretada, hombros rígidos) cuando estás molesto/a?"
  ]
};



// Inicialización
let puntajes = { Felicidad: 0, Tristeza: 0, Miedo: 0, Enojo: 0 };
let preguntaIndex = 0;

let etapa = "seleccion"; // "seleccion" o "sino"
let emocionPredominante = "";

const preguntaActualEl = document.getElementById("preguntaActual");
const opcionesContainer = document.getElementById("opcionesContainer");
const finalMessageEl = document.getElementById("finalMessage");

// Función para mostrar pregunta
function mostrarPregunta() {
  opcionesContainer.innerHTML = "";

  if (etapa === "seleccion") {
    if (preguntaIndex < preguntasIniciales.length) {
      const pregunta = preguntasIniciales[preguntaIndex];
      preguntaActualEl.innerText = pregunta.texto;

      pregunta.opciones.forEach(opcion => {
        const btn = document.createElement("button");
        btn.className = "btn btn-outline-primary opcion-btn mb-2";
        btn.innerText = `${opcion.letra}. ${opcion.texto}`;
        btn.onclick = () => {
          puntajes[opcion.emocion]++;
          preguntaIndex++;
          mostrarPregunta();
        };
        opcionesContainer.appendChild(btn);
      });
    } else {
      // Definir emoción ganadora
      emocionPredominante = Object.keys(puntajes).reduce((a, b) =>
        puntajes[a] >= puntajes[b] ? a : b
      );
      preguntaIndex = 0;
      etapa = "sino";
      mostrarPregunta();
    }
  } else if (etapa === "sino") {
    const preguntasFinales = preguntasSiNo[emocionPredominante];
    if (preguntaIndex < preguntasFinales.length) {
      preguntaActualEl.innerText = preguntasFinales[preguntaIndex];

      ["Sí", "No"].forEach(resp => {
        const btn = document.createElement("button");
        btn.className = "btn btn-outline-primary opcion-btn mb-2";
        btn.innerText = resp;
        btn.onclick = () => {
          preguntaIndex++;
          mostrarPregunta();
        };
        opcionesContainer.appendChild(btn);
      });
    } else {
      // Fin de preguntas → mostrar botón "Ver resultados"
      preguntaActualEl.classList.add("d-none");
      finalMessageEl.classList.remove("d-none");

      const botonResultados = document.createElement("button");
      botonResultados.className = "btn btn-success btn-lg mt-3";
      botonResultados.innerText = "Ver resultados";
      botonResultados.onclick = () => {
        // Redirige a la URL de Django, pasándole la emoción como query param
        window.location.href = `/resultado/?emocion=${encodeURIComponent(emocionPredominante)}`;
      };
      opcionesContainer.appendChild(botonResultados);
    }
  }
}

// Iniciar
mostrarPregunta();
