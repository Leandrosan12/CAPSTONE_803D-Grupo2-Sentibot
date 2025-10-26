from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
import json
import base64
from io import BytesIO
from PIL import Image
import requests

# ------------------------------
# Autenticación
# ------------------------------
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html", {"user": request.user})

def registro(request):
    return render(request, "registro.html")

def login(request):
    return render(request, "login.html")

def logout_view(request):
    return redirect("login")

# ------------------------------
# Páginas principales
# ------------------------------
def perfil(request):
    return render(request, 'perfil.html')

def camara(request):
    return render(request, "camara.html")

def extra(request):
    return render(request, 'extra.html')

def agenda_view(request):
    return render(request, 'agenda.html')

def modulo(request):
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    return render(request, 'modulo_profesor.html')

def alumnos(request):
    return render(request, 'modulo/alumnos.html')

def detalle_alumno(request, alumno_id):
    return render(request, 'modulo/detalle_alumno.html', {'alumno_id': alumno_id})

def escuelas(request):
    return render(request, 'modulo/escuelas.html')

def actividades(request):
    return render(request, 'actividades.html')

def mantenimiento(request):
    return render(request, 'mantenimiento.html')

def seguimiento(request):
    return render(request, 'seguimiento.html')

def lista_usuarios(request):
    return render(request, 'lista_usuarios.html')

def dashboard_emociones(request):
    return render(request, 'dashboard_emociones.html')

# ------------------------------
# API de predicción de emociones
# ------------------------------
def predict_emotion_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_base64 = data.get("image")

        if not image_base64:
            return JsonResponse({"label": "Null", "confidence": 0})

        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        try:
            image_bytes = base64.b64decode(image_base64)
            Image.open(BytesIO(image_bytes))
        except Exception as e:
            return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)})

        API_URL = "http://127.0.0.1:5000/predict_emotion"
        try:
            response = requests.post(API_URL, json={"image": image_base64}, timeout=5)
            result = response.json()
            label = result.get("label", "Sin reconocer")
            confidence = result.get("confidence", 0)
        except Exception as e:
            return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)})

        return JsonResponse({"label": label, "confidence": confidence})
