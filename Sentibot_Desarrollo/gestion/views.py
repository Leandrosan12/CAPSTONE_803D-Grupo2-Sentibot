from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Count
from django.db import connection
from gestion.models import Usuario, Emocion, EmocionReal, Sesion
User = get_user_model()


# ------------------------------
# Vistas de autenticación
# ------------------------------

def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html", {"user": request.user})


def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'El email ya está registrado'})

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return redirect('login')

    return render(request, 'registro.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('camara')
        else:
            return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ------------------------------
# Vistas principales
# ------------------------------

def perfil(request):
    return render(request, 'perfil.html')



def camara(request):
    return render(request, 'camara.html')
    return render(request, "camara.html")
def extra(request):
    return render(request, 'extra.html')

def agenda_view(request):
    return render(request, 'agenda.html')

# ------------------------------
# Modulo
# ------------------------------
def modulo(request):
    return render(request, 'modulo.html')

# ------------------------------
def dashboard(request):
    return render(request, "dashboard.html")


# ------------------------------
# LOGOUT
# ------------------------------
def logout_view(request):
    auth_logout(request)
    return redirect("login")

def actividades(request):
    return render(request, 'actividades.html')


# ------------------------------
# Vistas con datos
# ------------------------------

def emociones_data(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nombre_emocion, COUNT(*) as total 
            FROM gestion_emocion 
            GROUP BY nombre_emocion;
        """)
        rows = cursor.fetchall()

    data = {
        "labels": [row[0] for row in rows],
        "values": [row[1] for row in rows],
    }
    return JsonResponse(data)

# gestion/views.py
import json
import base64
import requests
from io import BytesIO
from django.http import JsonResponse
from PIL import Image

FASTAPI_URL = "https://negational-kerry-untoward.ngrok-free.dev/predict_emotion/"

def predict_emotion_view(request):
    """Proxy que recibe la imagen desde el front y la envía a FastAPI"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_base64 = data.get("image")

            if not image_base64:
                return JsonResponse({"emotion": "sin_reconocer", "confidence": 0})

            # Limpiar el encabezado base64
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]

            # Convertir base64 a bytes
            image_bytes = base64.b64decode(image_base64)

            # Enviar al servidor FastAPI
            files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
            response = requests.post(FASTAPI_URL, files=files, timeout=10)

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"emotion": "error_api", "confidence": 0})
        except Exception as e:
            return JsonResponse({"emotion": "error", "confidence": 0, "detail": str(e)})

    return JsonResponse({"error": "Método no permitido"}, status=405)

# gestion/views.py
from django.shortcuts import render
from .models import EmocionReal
from django.db.models import Count

def seguimiento(request):
    datos = EmocionReal.objects.values('emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion'] for d in datos]
    valores = [d['total'] for d in datos]

    return render(request, 'seguimiento.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })

from django.shortcuts import render
from .models import EmocionCamara

from django.db import connection
from django.shortcuts import render

from .models import Usuario

def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    return render(request, 'lista_usuarios.html', {'usuarios': datos})



def dashboard_emociones(request):
    # Ejecutamos la vista directamente
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_emociones_camara")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    context = {
        'emociones': datos
    }
    return render(request, 'dashboard_emociones.html', context)

def mantenimiento(request):
    return render(request, 'mantenimiento.html')

def extra(request):
    return render(request, 'extra.html')
