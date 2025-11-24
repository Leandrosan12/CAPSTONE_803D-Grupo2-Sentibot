# servidor.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Inicializar FastAPI
app = FastAPI(
    title="API de Detección de Emociones",
    description="Predice emociones a partir de una imagen facial",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo
print("Cargando modelo...")
modelo = load_model("modelo_emociones_v7 (3).keras", compile=False)
CLASSES = ['alegria', 'enojo', 'miedo', 'neutral', 'tristeza']
print("Modelo cargado correctamente ✅")

@app.get("/")
def home():
    return {"message": "✅ API de emociones activa. Usa /docs para probarla."}

@app.post("/predict_emotion/")
async def predict_emotion(file: UploadFile = File(...)):
    """
    Recibe una imagen (rostro) y devuelve la emoción detectada y su confianza.
    """
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)

    # Preprocesamiento igual al del entrenamiento
    img = cv2.resize(img, (48, 48))
    img = img.astype("float32") / 255.0
    img = img.reshape(1, 48, 48, 1)

    # Predicción
    pred = modelo.predict(img)
    idx = int(np.argmax(pred))
    conf = float(np.max(pred))

    return {
        "emotion": CLASSES[idx],
        "confidence": round(conf * 100, 2)
    }
