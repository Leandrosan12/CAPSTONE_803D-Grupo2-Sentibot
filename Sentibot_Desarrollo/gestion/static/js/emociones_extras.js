const tests = {
    "Alegría": [
        "¿Te sientes motivado/a para realizar tus actividades diarias?",
        "¿Disfrutas compartir momentos con otras personas?",
        "¿Te resulta fácil encontrar algo positivo en situaciones difíciles?",
        "¿Sueles dedicar tiempo a tus hobbies o pasatiempos favoritos?",
        "¿Te sientes satisfecho/a con los logros recientes que has tenido?"
    ],
    "Tristeza": [
        "¿Te sientes abatido/a durante el día?",
        "¿Necesitas apoyo de otras personas para sentirte mejor?",
        "¿Tienes dificultad para disfrutar tus actividades habituales?",
        "¿Prefieres estar solo/a para reflexionar?",
        "¿Te sientes decaído/a o sin energía?"
    ],
    "Miedo": [
        "¿Te sientes inseguro/a o ansioso/a actualmente?",
        "¿Evitas ciertas situaciones por temor?",
        "¿Tu mente se llena de preocupaciones frecuentes?",
        "¿Sientes tensión o nerviosismo en tu cuerpo?",
        "¿Sientes que necesitas protección o seguridad extra?"
    ],
    "Enojo": [
        "¿Te irritas fácilmente hoy?",
        "¿Sientes frustración por situaciones recientes?",
        "¿Te cuesta controlar tus impulsos?",
        "¿Quieres expresar tu enojo de alguna manera?",
        "¿Notas tensión física al estar enojado/a?"
    ],
    "Asco": [
        "¿Te sientes incómodo/a con algo que viste o experimentaste?",
        "¿Evitas ciertas personas o situaciones desagradables?",
        "¿Notas aversión hacia alimentos, olores o ambientes?",
        "¿Sientes rechazo ante algo específico?",
        "¿Deseas alejarte de lo que te incomoda?"
    ],
    "Neutral": [
        "¿Tu día ha sido rutinario sin grandes emociones?",
        "¿No sientes ni felicidad ni tristeza predominante?",
        "¿Te encuentras en un estado equilibrado emocionalmente?",
        "¿Tus decisiones hoy han sido calmadas y meditadas?",
        "¿Sientes estabilidad en tu ánimo?"
    ]
};

const significados = {
    "Alegría": "Energía alta, apertura social",
    "Tristeza": "Necesidad de apoyo o descanso",
    "Miedo": "Necesidad de seguridad o calma",
    "Enojo": "Necesidad de desahogo o justicia",
    "Asco": "Necesidad de distancia o límites",
    "Neutral": "Estado equilibrado y estable"
};

const recomendaciones = {
    "Alegría": [
        {icon:"🎶", text:"Escucha tu música favorita"},
        {icon:"🏃‍♂️", text:"Sal a caminar al aire libre"},
        {icon:"📖", text:"Comparte momentos positivos"}
    ],
    "Tristeza": [
        {icon:"📝", text:"Escribe tus sentimientos"},
        {icon:"💬", text:"Habla con alguien de confianza"},
        {icon:"🎨", text:"Realiza algo creativo"}
    ],
    "Miedo": [
        {icon:"🧘‍♂️", text:"Practica respiración profunda"},
        {icon:"📚", text:"Infórmate para sentir seguridad"},
        {icon:"🛋️", text:"Busca un lugar tranquilo y seguro"}
    ],
    "Enojo": [
        {icon:"🏃‍♀️", text:"Haz ejercicio físico"},
        {icon:"🖌️", text:"Canaliza la emoción creativamente"},
        {icon:"💨", text:"Respira profundamente y relájate"}
    ],
    "Asco": [
        {icon:"🧼", text:"Mantente alejado de lo que incomoda"},
        {icon:"🧘‍♀️", text:"Práctica mindfulness"},
        {icon:"📖", text:"Realiza actividades agradables"}
    ],
    "Neutral": [
        {icon:"📚", text:"Lee un libro interesante"},
        {icon:"☕", text:"Tómate un momento para ti"},
        {icon:"🧘‍♀️", text:"Medita o practica mindfulness"}
    ]
};

let indicePregunta = 0;
let respuestas = [];
let emocionActual = "";

function iniciarTest(emocion){
    emocionActual = emocion;
    indicePregunta = 0;
    respuestas = [];
    document.getElementById('emocionSeleccionada').textContent = "Emoción seleccionada: " + emocion;
    document.getElementById('testSection').style.display = "block";
    document.getElementById('resultadoDiv').style.display = "none";
    mostrarPregunta();
    window.scrollTo({top:0, behavior:'smooth'});
}

function mostrarPregunta(){
    const preguntas = tests[emocionActual];
    if(indicePregunta < preguntas.length){
        document.getElementById('preguntaTexto').textContent = preguntas[indicePregunta];
        const container = document.getElementById('opcionesContainer');
        container.innerHTML = '';
        ["Sí","No"].forEach(op => {
            const btn = document.createElement('button');
            btn.className = "btn btn-outline-primary opcion-btn";
            btn.textContent = op;
            btn.onclick = () => seleccionarRespuesta(op);
            container.appendChild(btn);
        });
    } else {
        mostrarResultado();
    }
}

function seleccionarRespuesta(respuesta){
    respuestas.push(respuesta);
    indicePregunta++;
    mostrarPregunta();
}

function mostrarResultado(){
    document.getElementById('preguntaTexto').textContent = '';
    document.getElementById('opcionesContainer').innerHTML = '';
    document.getElementById('resultadoDiv').style.display = 'block';
    document.getElementById('emocionFinal').textContent = "Tu emoción predominante es: " + emocionActual;
    document.getElementById('significado').textContent = significados[emocionActual];

    const cont = document.getElementById('recomendaciones');
    cont.innerHTML = '';
    recomendaciones[emocionActual].forEach(r => {
        const div = document.createElement('div');
        div.className = "recommendation-card";
        div.innerHTML = `<span>${r.icon}</span>${r.text}`;
        cont.appendChild(div);
    });

    window.scrollTo({top:0, behavior:'smooth'});
}
