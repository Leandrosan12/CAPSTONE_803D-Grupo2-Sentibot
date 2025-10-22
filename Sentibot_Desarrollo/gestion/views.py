from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
<<<<<<< HEAD
from django.http import JsonResponse
=======
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
>>>>>>> eff6f01c27b06bbbd1392fc743d0f63bccb3d120
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
<<<<<<< HEAD
=======
    return render(request, 'camara.html')
>>>>>>> eff6f01c27b06bbbd1392fc743d0f63bccb3d120
    return render(request, "camara.html")

def extra(request):
    return render(request, 'extra.html')

def agenda_view(request):
    return render(request, 'agenda.html')

# ------------------------------
# Módulos principales
# ------------------------------
def modulo(request):
    # Llama a gestion/templates/modulo/modulo.html
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    profesores = [
        {'id': 1, 'nombre': 'Juan Torres', 'rut': '18.234.567-9', 'correo': 'juan.torres@duocuc.cl', 'telefono': '+569 87654321', 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'María Rojas', 'rut': '17.123.456-0', 'correo': 'maria.rojas@duocuc.cl', 'telefono': '+569 91234567', 'sede': 'Melipilla'},
    ]
    return render(request, 'modulo_profesor.html', {'profesores': profesores})

# ------------------------------
<<<<<<< HEAD
# Módulo Alumnos y Escuelas
# ------------------------------
def alumnos(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, first_name, last_name, email, sede FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        alumnos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    return render(request, 'alumnos.html', {'alumnos': alumnos})
=======
def dashboard(request):
    return render(request, "dashboard.html")
>>>>>>> eff6f01c27b06bbbd1392fc743d0f63bccb3d120

def detalle_alumno(request, alumno_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario WHERE id = %s", [alumno_id])
        columnas = [col[0] for col in cursor.description]
        alumno = dict(zip(columnas, cursor.fetchone()))
    return render(request, 'detalle_alumno.html', {'alumno': alumno})

def escuelas(request):
    escuelas = [
        {'id': 1, 'nombre': 'Escuela de Ingeniería', 'carreras': ['Informática', 'Civil', 'Industrial'], 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'Escuela de Construcción', 'carreras': ['Construcción', 'Arquitectura'], 'sede': 'Quilpué'},
        {'id': 3, 'nombre': 'Escuela de Medicina', 'carreras': ['Medicina', 'Enfermería'], 'sede': 'Concepción'},
    ]
    return render(request, 'escuelas.html', {'escuelas': escuelas})

# ------------------------------
# Actividades
# ------------------------------
def actividades(request):
    return render(request, 'actividades.html')

# ------------------------------
# Datos y seguimiento
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

import json
import base64
from io import BytesIO
from PIL import Image
from django.http import JsonResponse
from .ml_model import predict_emotion

def predict_emotion_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_base64 = data.get("image")

        if not image_base64:
            return JsonResponse({"label": "Null", "confidence": 0})

        # Quitar encabezado data:image/png;base64,
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes)).convert("L")  # Escala de grises
        except Exception as e:
            return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)})

        label, confidence = predict_emotion(image)
        return JsonResponse({"label": label, "confidence": confidence})

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

def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})

def mantenimiento(request):
    return render(request, 'mantenimiento.html')
