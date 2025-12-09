# Sentibot: Análisis de Sentimientos Multicanal

Este repositorio contiene el proyecto **Sentibot**, un capstone orientado a construir un sistema de **análisis de sentimientos** que integra modelos de deep learning, notebooks exploratorios y una API de inferencia, junto a materiales de las distintas fases del desarrollo del proyecto.

---

## Objetivos del Proyecto

- Clasificar sentimiento: Detectar y clasificar el sentimiento de textos (positivo, negativo, neutro) usando un modelo de aprendizaje profundo.
- Pipeline reproducible: Proveer notebooks y scripts para limpieza, entrenamiento y evaluación del modelo.
- API de servicio: Exponer el modelo como un servicio para integrar con aplicaciones web o bots.
- Entrega por fases: Documentar el avance en etapas con presentaciones y materiales de soporte.

---

## Estructura del Repositorio

- **Fase1, Fase2, Fase3:**  
  Carpetas con materiales y entregables de cada etapa del proyecto (presentaciones, avances, documentación).

- **ModeloCNN-API:**  
  Implementación del modelo CNN y la API de inferencia para desplegar el clasificador como servicio.

- **Sentibot_Desarrollo:**  
  Código y activos de desarrollo (componentes web, integración y pruebas).

- **Otros archivos:**  
  Registros auxiliares y archivos internos de control del proyecto.

Nota: El código está mayormente desarrollado en Jupyter Notebook, además de Python, HTML, JavaScript y CSS.

---

## Tecnologías Principales

- Jupyter Notebook
- Python
- HTML / CSS / JavaScript

### Distribución aproximada de lenguajes

- Jupyter Notebook: ~73%  
- Python: ~10%  
- HTML: ~9%  
- JavaScript: ~5%  
- CSS: ~2%  

---

## Requisitos y Configuración

- Python 3.10+ recomendado
- Entorno virtual con venv o conda

### Dependencias típicas

Modelado:
- numpy
- pandas
- scikit-learn
- tensorflow / keras o pytorch

API:
- fastapi o flask
- uvicorn / gunicorn

NLP:
- nltk
- spacy

### Instalación

1. Clonar el repositorio  
2. Crear y activar el entorno virtual  
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar los paquetes manualmente.

---

## Uso del Proyecto

### Entrenamiento y Experimentación

Revisar los notebooks en Fase1, Fase2 y Fase3 para:

- Limpieza y preparación de datos  
- Entrenamiento del modelo CNN  
- Evaluación con métricas (accuracy, F1, matrices de confusión, curvas ROC)

---

### Inferencia vía API

1. Acceder a la carpeta `ModeloCNN-API`
2. Ejecutar el servidor (ejemplo con FastAPI):

```bash
uvicorn app:app --reload
```

### Endpoint principal

POST /predict

Body JSON:
```json
{
  "text": "Me encantó el servicio, volvería sin dudas."
}
```

Respuesta:
```json
{
  "label": "positivo",
  "score": 0.94
}
```

---

### Front-end / Demo

En la carpeta Sentibot_Desarrollo se incluyen archivos HTML, JS y CSS para una interfaz básica que consume la API y muestra los resultados del análisis de sentimiento.

---

## Buenas Prácticas

- Versionado de datos y modelos
- Preprocesamiento consistente
- Uso de métricas F1, precisión y recall
- Análisis de errores
- Despliegue con Docker y configuración CORS

---

## Estado del Proyecto y Colaboradores

- Actividad reciente por fases
- Tres contribuidores principales

---

## Licencia

Actualmente el repositorio no especifica licencia.  
Se recomienda añadir una licencia como MIT o Apache 2.0.

---

## Contribuir

- Abrir issues para mejoras o errores
- Crear Pull Requests con descripción clara
- Seguir PEP8 en Python
- Buenas prácticas en notebooks y front-end

---

## Próximos Pasos

- Agregar README específicos por carpeta
- Publicar requirements.txt
- Documentar datasets utilizados
- Comparar CNN con modelos basados en Transformers (BERT, etc.)

---

Este README fue generado a partir de la estructura del repositorio público  
CAPSTONE_803D-Grupo2-Sentibot y puede requerir ajustes según el contenido interno de cada carpeta.
