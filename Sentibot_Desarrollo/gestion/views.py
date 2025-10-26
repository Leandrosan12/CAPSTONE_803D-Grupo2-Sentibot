from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import JsonResponse
from django.db.models import Count
from django.db import connection
<<<<<<< HEAD
import json
import base64
from io import BytesIO
from PIL import Image
import requests  # Para llamar a la API externa

User = get_user_model()
=======
from gestion.models import Usuario, Emocion, EmocionReal, Sesion
>>>>>>> origin/LeandroFabio

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

<<<<<<< HEAD

def camara(request):
    return render(request, 'camara.html')

=======
def camara(request):
    return render(request, "camara.html")
>>>>>>> origin/LeandroFabio

def extra(request):
    return render(request, 'extra.html')


def agenda_view(request):
    return render(request, 'agenda.html')

<<<<<<< HEAD

=======
# ------------------------------
# Módulos principales
# ------------------------------
>>>>>>> origin/LeandroFabio
def modulo(request):
    # Llama a gestion/templates/modulo/modulo.html
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    profesores = [
        {'id': 1, 'nombre': 'Juan Torres', 'rut': '18.234.567-9', 'correo': 'juan.torres@duocuc.cl', 'telefono': '+569 87654321', 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'María Rojas', 'rut': '17.123.456-0', 'correo': 'maria.rojas@duocuc.cl', 'telefono': '+569 91234567', 'sede': 'Melipilla'},
    ]
    return render(request, 'modulo_profesor.html', {'profesores': profesores})

<<<<<<< HEAD

def dashboard(request):
    return render(request, "dashboard.html")
=======
# ------------------------------
# Módulo Alumnos y Escuelas
# ------------------------------
def alumnos(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, first_name, last_name, email, sede FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        alumnos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    return render(request, 'alumnos.html', {'alumnos': alumnos})
>>>>>>> origin/LeandroFabio

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

<<<<<<< HEAD
def actividades(request):
    return render(request, 'actividades.html')


def mantenimiento(request):
    return render(request, 'mantenimiento.html')


=======
# ------------------------------
# Actividades
# ------------------------------
def actividades(request):
    return render(request, 'actividades.html')

>>>>>>> origin/LeandroFabio
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

<<<<<<< HEAD

# ------------------------------
# Predicción de emociones vía API externa
# ------------------------------

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
            # Decodificar y abrir la imagen
            image_bytes = base64.b64decode(image_base64)
            Image.open(BytesIO(image_bytes))  # Solo validar que es imagen
        except Exception as e:
            return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)})

        # Llamada al API externa
        API_URL = "http://127.0.0.1:5000/predict_emotion"  # Cambia a tu URL real si la API está en otro host
        try:
            response = requests.post(API_URL, json={"image": image_base64}, timeout=5)
            result = response.json()
            label = result.get("label", "Sin reconocer")
            confidence = result.get("confidence", 0)
        except Exception as e:
            return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)})

        return JsonResponse({"label": label, "confidence": confidence})


# ------------------------------
# Seguimiento emociones
# ------------------------------

=======
>>>>>>> origin/LeandroFabio
def seguimiento(request):
    from .models import EmocionReal
    datos = EmocionReal.objects.values('emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'seguimiento.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })

<<<<<<< HEAD

=======
>>>>>>> origin/LeandroFabio
def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})

<<<<<<< HEAD

def dashboard_emociones(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_emociones_camara")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    context = {
        'emociones': datos
    }
    return render(request, 'dashboard_emociones.html', context)
=======
def mantenimiento(request):
    return render(request, 'mantenimiento.html')
>>>>>>> origin/LeandroFabio
