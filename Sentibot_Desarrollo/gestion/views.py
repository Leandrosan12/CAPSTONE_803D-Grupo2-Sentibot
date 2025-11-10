# Django shortcuts y utilidades
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Autenticación
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
User = get_user_model()

# Modelos y base de datos
from django.db.models import Count, Avg
from django.db import connection
from .models import Sesion, EmocionCamara, Usuario
from gestion.models import Usuario as GestionUsuario, Emocion, EmocionReal, Sesion as GestionSesion


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html", {"user": request.user})
# views.py (asegúrate de tener los imports)
import random
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def enviar_codigo(request):
    email = request.GET.get('correo')
    if not email:
        return JsonResponse({'error': 'Correo no proporcionado'}, status=400)

    # 1) Si el correo ya está registrado, no enviamos código
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'Este correo ya está registrado.'}, status=400)

    # 2) Generar código y guardar en sesión con expiración (10 minutos)
    codigo = str(random.randint(100000, 999999))
    request.session['codigo_verificacion'] = codigo
    request.session['correo_verificacion'] = email
    # Guardamos la expiración como ISO o timestamp
    expiracion = timezone.now() + timedelta(minutes=10)
    request.session['codigo_expira'] = expiracion.isoformat()

    # 3) Intentar enviar correo (capturamos errores)
    try:
        send_mail(
            'Código de verificación',
            f'Tu código de verificación es: {codigo}',
            None,               # Dejar None para que use DEFAULT_FROM_EMAIL si lo tienes configurado
            [email],
            fail_silently=False,
        )
    except Exception as e:
        logger.exception("Error enviando correo de verificación")
        # Limpia la sesión para no dejar datos inconsistentes
        request.session.pop('codigo_verificacion', None)
        request.session.pop('correo_verificacion', None)
        request.session.pop('codigo_expira', None)
        return JsonResponse({
            'error': 'No se pudo enviar el correo. Verifica la configuración SMTP.'
        }, status=500)

    return JsonResponse({'mensaje': 'Código enviado correctamente al correo. Revisa tu bandeja de entrada.'})


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



@login_required(login_url='login')  # ajusta la URL si la llamas distinto
def camara(request):
    # Obtener o crear sesión activa solo para usuarios autenticados
    sesion = Sesion.objects.filter(usuario=request.user, fecha_fin__isnull=True).first()
    if not sesion:
        sesion = Sesion.objects.create(usuario=request.user)  # ✅ se elimina "inicio", se llena solo con auto_now_add
    return render(request, "camara.html", {"sesion_id": sesion.id})

def extra(request):
    return render(request, 'extra.html')

def agenda_view(request):
    return render(request, 'agenda.html')

# ------------------------------
# Módulos principales
# ------------------------------
def modulo(request):
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    profesores = [
        {'id': 1, 'nombre': 'Juan Torres', 'rut': '18.234.567-9', 'correo': 'juan.torres@duocuc.cl', 'telefono': '+569 87654321', 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'María Rojas', 'rut': '17.123.456-0', 'correo': 'maria.rojas@duocuc.cl', 'telefono': '+569 91234567', 'sede': 'Melipilla'},
    ]
    return render(request, 'modulo_profesor.html', {'profesores': profesores})

from django.shortcuts import render
from .models import Usuario  # o el modelo que uses para usuarios

def alumnos(request):
    usuarios = Usuario.objects.all()  # Trae todos los usuarios
    return render(request, 'modulo/alumnos.html', {'usuarios': usuarios})


# views.py
from django.shortcuts import render, get_object_or_404
from .models import Usuario  # tu modelo personalizado

def detalle_alumno(request, id):
    alumno = get_object_or_404(Usuario, id=id)
    return render(request, 'modulo/detalle_alumno.html', {'alumno': alumno})

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

def mantenimiento(request):
    return render(request, 'mantenimiento.html')


def seguimiento(request):
    # Agregamos las emociones totales por nombre
    emociones_agg = EmocionCamara.objects.values('nombre_emocion').annotate(cantidad=Count('id'))
    emociones = list(emociones_agg)  # [{'nombre_emocion': 'Feliz', 'cantidad': 5}, ...]

    # Agregamos datos por usuario
    datos_usuarios = []
    usuarios = Usuario.objects.all()
    for u in usuarios:
        sesiones = Sesion.objects.filter(usuario=u)
        emociones_usuario = EmocionCamara.objects.filter(sesion__in=sesiones)
        emociones_count = emociones_usuario.values('nombre_emocion').annotate(cantidad=Count('id'))
        datos_usuarios.append({
            'usuario': u.username,
            'emociones': list(emociones_count)
        })

    return render(request, 'seguimiento.html', {
        'emociones': emociones,
        'datos_usuarios': datos_usuarios
    })







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
# gestion/views.py
import json
import base64
import requests
from io import BytesIO
from django.http import JsonResponse
from PIL import Image

FASTAPI_URL = "https://negational-kerry-untoward.ngrok-free.dev/predict_emotion/"

=======
>>>>>>> dfebbc25729eec6fa73775de26b91c69c8d30550
def predict_emotion_view(request):
    """Proxy que recibe la imagen desde el front y la envía a FastAPI"""
    if request.method == "POST":
<<<<<<< HEAD
=======
        data = json.loads(request.body)
        image_base64 = data.get("image")

        if not image_base64:
            return JsonResponse({"label": "Null", "confidence": 0})

        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

>>>>>>> dfebbc25729eec6fa73775de26b91c69c8d30550
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

# ------------------------------
# Seguimiento Emociones
# ------------------------------
def seguimiento(request):
    datos = EmocionReal.objects.values('emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'seguimiento.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })

# ------------------------------
# Nueva vista: Dashboard Emociones
# ------------------------------
def dashboard_emociones(request):
    datos = EmocionReal.objects.values('emocion__nombre_emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion__nombre_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'dashboard_emociones.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })

# ------------------------------
# Lista de usuarios
# ------------------------------
def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})

# ------------------------------
# Mantenimiento
# ------------------------------
def mantenimiento(request):
    return render(request, 'mantenimiento.html')
# ------------------------------
#registro
# ------------------------------
def registro(request):
    return render(request, 'registro.html')
