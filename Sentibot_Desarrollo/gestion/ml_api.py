import requests
from PIL import Image
import io

API_URL = "https://negational-kerry-untoward.ngrok-free.dev/predict_emotion/"

def predict_emotion_from_image(pil_image):
    """
    Envía una imagen PIL a la API remota de emociones y devuelve label y confianza.
    """
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG")
    buf.seek(0)
    files = {"file": ("frame.jpg", buf, "image/jpeg")}

    try:
        response = requests.post(API_URL, files=files, timeout=8)
        if response.status_code == 200:
            data = response.json()
            return data.get("emotion", "Sin reconocer"), float(data.get("confidence", 0.0))
        else:
            return "Error", 0.0
    except Exception as e:
        return "Sin conexión", 0.0
