# ml_model.py
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'models', 'sentibotv2.h5')  # ajusta según tu carpeta
model = load_model(model_path)

# Define las clases según tu entrenamiento
CLASSES = ['Sorprendido', 'Enojado', 'Feliz','Neutral', 'Triste' ]  # Ajusta según tu modelo

def predict_emotion(image):
    image = image.convert('L')  # Escala de grises
    image = image.resize((48, 48))  # Ajusta según tu input
    image_array = img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0) / 255.0
    prediction = model.predict(image_array)
    label = CLASSES[np.argmax(prediction)]
    confidence = float(np.max(prediction)) * 100
    
    return label, confidence
