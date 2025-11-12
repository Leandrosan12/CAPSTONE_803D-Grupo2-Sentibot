from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse
import json, base64, requests
from .models import Usuario, Sesion, Emocion, EmocionCamara, EmocionReal, Actividad

User = get_user_model()
FASTAPI_URL = "https://negational-kerry-untoward.ngrok-free.dev/predict_emotion/"

# ------------------------------
# LOGIN / LOGOUT
# ------------------------------
def login(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        user = authenticate(request, email=email, password=password)
        if user and user.is_active:
            auth_login(request, user)
            return redirect('opciones')
        return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})
    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('login')


def opciones(request):
    return render(request, 'opciones.html')


# ------------------------------
# REGISTRO
# ------------------------------
def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'Correo ya registrado'})

        username = email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        auth_login(request, user)
        return redirect('camara')
    return render(request, 'registro.html')


# ------------------------------
# VISTAS PRINCIPALES
# ------------------------------
@login_required(login_url='login')
def home(request):
    return render(request, "home.html", {"user": request.user})


@login_required(login_url='login')
def perfil(request):
    return render(request, 'perfil.html')


@login_required(login_url='login')
def camara(request):
    sesion = Sesion.objects.filter(usuario=request.user, fecha_fin__isnull=True).first()
    if not sesion:
        sesion = Sesion.objects.create(usuario=request.user)
    return render(request, "camara.html", {"sesion_id": sesion.id})


def extra(request):
    return render(request, 'extra.html')


def agenda(request):
    return render(request, 'agenda.html')


# ------------------------------
# MODULOS
# ------------------------------
def modulo(request):
    return render(request, 'modulo/modulo.html')


def modulo_profesor(request):
    profesores = [
        {'id': 1, 'nombre': 'Juan Torres', 'rut': '18.234.567-9', 'correo': 'juan.torres@duocuc.cl', 'telefono': '+569 87654321', 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'María Rojas', 'rut': '17.123.456-0', 'correo': 'maria.rojas@duocuc.cl', 'telefono': '+569 91234567', 'sede': 'Melipilla'},
    ]
    return render(request, 'modulo_profesor.html', {'profesores': profesores})


def alumnos(request):
    usuarios = Usuario.objects.all()
    return render(request, 'modulo/alumnos.html', {'usuarios': usuarios})


def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Usuario, id=alumno_id)
    return render(request, 'modulo/detalle_alumno.html', {'alumno': alumno})


def escuelas(request):
    escuelas = [
        {'id': 1, 'nombre': 'Escuela de Ingeniería', 'carreras': ['Informática', 'Civil', 'Industrial'], 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'Escuela de Construcción', 'carreras': ['Construcción', 'Arquitectura'], 'sede': 'Quilpué'},
        {'id': 3, 'nombre': 'Escuela de Medicina', 'carreras': ['Medicina', 'Enfermería'], 'sede': 'Concepción'},
    ]
    return render(request, 'escuelas.html', {'escuelas': escuelas})


# ------------------------------
# ACTIVIDADES
# ------------------------------
@login_required
def actividades(request):
    return render(request, 'actividades.html')


def mantenimiento(request):
    return render(request, 'mantenimiento.html')


# ------------------------------
# EMOCIONES
# ------------------------------
def emociones_data(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre_emocion, COUNT(*) FROM gestion_emocion GROUP BY nombre_emocion")
        rows = cursor.fetchall()
    data = {"labels": [r[0] for r in rows], "values": [r[1] for r in rows]}
    return JsonResponse(data)


def seguimiento(request):
    datos = EmocionReal.objects.values('emocion__nombre_emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion__nombre_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'seguimiento.html', {'emociones_labels': etiquetas, 'emociones_counts': valores})


def dashboard_emociones(request):
    datos = EmocionReal.objects.values('emocion__nombre_emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion__nombre_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'dashboard_emociones.html', {'emociones_labels': etiquetas, 'emociones_counts': valores})


# ------------------------------
# PROCESAR EMOCIÓN CÁMARA
# ------------------------------
import json
from django.views.decorators.csrf import csrf_exempt  
@login_required
def procesar_emocion_camara(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id, usuario=request.user)

    # Parsear JSON del request
    data = json.loads(request.body)
    emocion_dominante = data.get("emocion", "Neutral")
    porcentaje = data.get("porcentaje", 0.0)

    # Buscar emoción en tabla Emocion
    emocion_obj = Emocion.objects.filter(nombre_emocion__iexact=emocion_dominante).first()

    if emocion_obj:
        EmocionReal.objects.create(
            sesion=sesion,
            emocion=emocion_obj,
            tipo_emocion=emocion_dominante,
            porcentaje=round(porcentaje, 2)
        )

    sesion.fecha_fin = timezone.now()
    sesion.save()

    return redirect("mostrar_actividades", emocion_nombre=emocion_dominante)


@login_required
def seleccionar_emocion(request, emocion_nombre):
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=emocion_nombre)
    sesion, _ = Sesion.objects.get_or_create(usuario=request.user, fecha_fin__isnull=True)
    EmocionReal.objects.create(sesion=sesion, emocion=emocion, tipo_emocion=emocion.nombre_emocion)
    return redirect('mostrar_actividades', emocion_nombre=emocion.nombre_emocion)


from random import randint, sample

@login_required
def mostrar_actividades(request, emocion_nombre):
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=emocion_nombre)
    
    # Actividades de la emoción detectada
    actividades_principal = list(Actividad.objects.filter(emocion=emocion))
    
    # Actividades de otras emociones (máx. 2)
    otras_actividades = list(Actividad.objects.exclude(emocion=emocion))
    otras_actividades = sample(otras_actividades, min(2, len(otras_actividades)))
    
    recomendaciones = []

    # Actividades principales (80-100%)
    for act in actividades_principal:
        recomendaciones.append({
            'actividad': act,
            'porcentaje': randint(80, 100),
        })
    
    # Actividades secundarias (30-50%)
    for act in otras_actividades:
        recomendaciones.append({
            'actividad': act,
            'porcentaje': randint(30, 50),
        })

    # Ordenar por porcentaje descendente
    recomendaciones.sort(key=lambda x: x['porcentaje'], reverse=True)

    # Calcular el porcentaje máximo
    max_porcentaje = max([rec['porcentaje'] for rec in recomendaciones]) if recomendaciones else 0

    return render(request, 'actividades.html', {
        'emocion': emocion,
        'recomendaciones': recomendaciones,
        'max_porcentaje': max_porcentaje,  # para usar en el template
    })



# ------------------------------
# PREDICT EMOTION (API)
# ------------------------------
def predict_emotion_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data = json.loads(request.body)
        image_base64 = data.get("image")
        if not image_base64:
            return JsonResponse({"emotion": "sin_reconocer", "confidence": 0})
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)
        files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
        response = requests.post(FASTAPI_URL, files=files, timeout=10)
        return JsonResponse(response.json() if response.status_code == 200 else {"emotion": "error_api", "confidence": 0})
    except Exception as e:
        return JsonResponse({"emotion": "error", "confidence": 0, "detail": str(e)})
    
from django.shortcuts import render, redirect
from .models import EncuestaSatisfaccion

from django.shortcuts import render, redirect
from .models import EncuestaSatisfaccion

def encuesta_satisfaccion(request):
    if request.method == 'POST':
        utilidad = request.POST.get('utilidad')
        recomendacion = request.POST.get('recomendacion')
        comentario = request.POST.get('comentario', '')

        if utilidad and recomendacion:
            EncuestaSatisfaccion.objects.create(
                utilidad=utilidad,
                recomendacion=int(recomendacion),
                comentario=comentario
            )
            return redirect('opciones')

    return render(request, 'encuesta_satisfaccion.html')