# ml_model.py
import os
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array

# Intentamos importar Keras, si falla usamos predicciones ficticias
try:
    from tensorflow.keras.models import load_model
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False

# Carpeta base y ruta del modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'models', 'sentibotv2_actualizado.h5')  # archivo actualizado

# Clases de salida
CLASSES = ['Sorprendido', 'Enojado', 'Feliz', 'Triste', 'Neutral']

# Intentar cargar el modelo si está disponible
if MODEL_AVAILABLE and os.path.exists(model_path):
    model = load_model(model_path)
    MODEL_READY = True
else:
    model = None
    MODEL_READY = False

def predict_emotion(image):
    """
    Recibe una imagen PIL, la procesa y devuelve la emoción predicha y su confianza.
    Si el modelo no está disponible, devuelve valores ficticios.
    """
    if not MODEL_READY:
        # Predicción ficticia
        return "Neutral", 100.0

    # Convertir a escala de grises y redimensionar
    image = image.convert('L')
    image = image.resize((48, 48))  # Ajusta según el input de tu modelo

    # Convertir a array y normalizar
    image_array = img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0) / 255.0

    # Predicción real
    prediction = model.predict(image_array)
    label = CLASSES[np.argmax(prediction)]
    confidence = float(np.max(prediction)) * 100

    return label, confidence
