# gestion/views.py
# ------------------------------
# Imports
# ------------------------------
import json
import logging
import random
import base64
from io import BytesIO
from datetime import timedelta
from random import randint, sample

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Avg, F
from django.db import connection
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from PIL import Image
import requests

# Modelos
from .models import (
    Usuario, Emocion, EmocionReal, EmocionCamara,
    Sesion, Escuela, RespuestaEncuesta
)

logger = logging.getLogger(__name__)
User = get_user_model()

# ------------------------------
# HOME / AUTENTICACIÓN
# ------------------------------
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html", {"user": request.user})

def login(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('camara')
        return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

# ------------------------------
# PERFIL
# ------------------------------
@login_required(login_url='login')
def perfil(request):
    return render(request, 'perfil.html')

# ------------------------------
# ENVÍO / VALIDACIÓN DE CÓDIGO
# ------------------------------
@require_GET
def enviar_codigo(request):
    correo = request.GET.get('correo')
    if not correo:
        return JsonResponse({'error': 'Correo requerido'}, status=400)

    if Usuario.objects.filter(email__iexact=correo).exists():
        return JsonResponse({'error': 'Este correo ya está registrado.'}, status=400)

    codigo = f"{random.randint(100000, 999999):06d}"
    expiracion = timezone.now() + timedelta(minutes=10)

    request.session['codigo_verificacion'] = codigo
    request.session['correo_verificacion'] = correo
    request.session['codigo_expira'] = expiracion.isoformat()
    request.session.save()

    subject = 'Código de verificación'
    message = f'Tu código de verificación es: {codigo}\n\nExpira en 10 minutos.'
    from_email = getattr(settings, 'EMAIL_HOST_USER', None)

    try:
        send_mail(subject, message, from_email, [correo], fail_silently=False)
        logger.info("Código %s enviado a %s", codigo, correo)
        return JsonResponse({'mensaje': 'Código enviado al correo.'})
    except Exception as e:
        logger.exception("Error enviando correo a %s: %s", correo, e)
        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)
        return JsonResponse({'error': 'No se pudo enviar el correo.'}, status=500)

@require_POST
def validar_codigo(request):
    try:
        payload = json.loads(request.body)
        correo = (payload.get('correo') or '').strip().lower()
        codigo = (payload.get('codigo') or '').strip()
    except Exception:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    codigo_sesion = request.session.get('codigo_verificacion')
    correo_sesion = (request.session.get('correo_verificacion') or '').lower()
    codigo_expira_iso = request.session.get('codigo_expira')

    if not (codigo_sesion and correo_sesion and codigo_expira_iso):
        return JsonResponse({"ok": False, "error": "No hay un código de verificación válido."}, status=400)

    if correo != correo_sesion:
        return JsonResponse({"ok": False, "error": "El correo no coincide con el verificado."}, status=400)

    try:
        expiracion = parse_datetime(codigo_expira_iso)
        if timezone.is_naive(expiracion):
            expiracion = timezone.make_aware(expiracion, timezone.get_current_timezone())
        now = timezone.now()
        if timezone.is_naive(now):
            now = timezone.make_aware(now, timezone.get_current_timezone())
    except Exception:
        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)
        return JsonResponse({"ok": False, "error": "Error en el proceso de verificación."}, status=400)

    if now > expiracion:
        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)
        return JsonResponse({"ok": False, "error": "El código ha expirado."}, status=400)

    if codigo != codigo_sesion:
        return JsonResponse({"ok": False, "error": "Código inválido."}, status=400)

    return JsonResponse({"ok": True})

# ------------------------------
# REGISTRO
# ------------------------------
def registro(request):
    if request.method == "POST":
        email = (request.POST.get('correo') or '').strip()
        password = request.POST.get('contrasena')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        codigo = (request.POST.get('codigo') or '').strip()
        escuela_id = request.POST.get('escuela')

        codigo_sesion = request.session.get('codigo_verificacion')
        correo_sesion = request.session.get('correo_verificacion')
        codigo_expira_iso = request.session.get('codigo_expira')

        if not (codigo_sesion and correo_sesion and codigo_expira_iso):
            return render(request, 'registro.html', {
                'error': 'No hay un código de verificación válido.',
                'escuelas': Escuela.objects.all()
            })

        if email.lower() != correo_sesion.lower():
            return render(request, 'registro.html', {
                'error': 'El correo no coincide con el verificado.',
                'escuelas': Escuela.objects.all()
            })

        expiracion = parse_datetime(codigo_expira_iso)
        if timezone.is_naive(expiracion):
            expiracion = timezone.make_aware(expiracion, timezone.get_current_timezone())

        if timezone.now() > expiracion:
            for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
                request.session.pop(key, None)
            return render(request, 'registro.html', {'error': 'Código expirado', 'escuelas': Escuela.objects.all()})

        if codigo != codigo_sesion:
            return render(request, 'registro.html', {'error': 'Código inválido', 'escuelas': Escuela.objects.all()})

        if Usuario.objects.filter(email__iexact=email).exists():
            return render(request, 'registro.html', {'error': 'El email ya está registrado', 'escuelas': Escuela.objects.all()})

        user = Usuario.objects.create_user(
            email=email, password=password, first_name=first_name, last_name=last_name, username=email
        )

        if escuela_id:
            try:
                escuela = Escuela.objects.get(id=escuela_id)
                user.escuela = escuela
                user.save()
            except Escuela.DoesNotExist:
                pass

        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)

        return redirect('login')

    return render(request, 'registro.html', {'escuelas': Escuela.objects.all()})

# ------------------------------
# MÓDULOS PRINCIPALES
# ------------------------------
def modulo(request):
    return render(request, 'modulo/modulo.html')
    return render(request, "camara.html", {"sesion_id": sesion.id})




@login_required
def extra(request):
    # Cerrar sesiones previas abiertas
    Sesion.objects.filter(usuario=request.user, activa=True).update(activa=False, fecha_fin=timezone.now())

    # Crear nueva sesión activa
    sesion = Sesion.objects.create(usuario=request.user, activa=True)

    emociones = Emocion.objects.all()
    return render(request, 'extra.html', {'emociones': emociones, 'sesion_id': sesion.id})



def agenda(request):
    return render(request, 'agenda.html')


# ============================================================
# MÓDULOS
# ============================================================
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


# ============================================================
# ACTIVIDADES
# ============================================================
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Actividad, Emocion

@login_required
def actividades(request):
    # Obtener la emoción de la query string
    emocion_param = request.GET.get('emocion', 'Neutral')

    # Opcional: mapear nombres de emoción si tus modelos usan nombres distintos
    emocion_map = {
        "Felicidad": "Alegría",
        "Tristeza": "Tristeza",
        "Miedo": "Miedo",
        "Enojo": "Enojo"
    }
    nombre_emocion = emocion_map.get(emocion_param, "Neutral")

    # Obtener la emoción
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=nombre_emocion)

    # Filtrar actividades según la emoción
    actividades = Actividad.objects.filter(emocion=emocion)

    # Crear recomendaciones "ficticias" para usar barra de porcentaje
    recomendaciones = [
        {"actividad": act, "porcentaje": 100}  # Puedes ajustar el porcentaje según tu lógica
        for act in actividades
    ]

    contexto = {
        "emocion": emocion,
        "recomendaciones": recomendaciones,
        "max_porcentaje": 100  # Para tu template de barras
    }

    return render(request, "actividades.html", contexto)




def mantenimiento(request):
    return render(request, 'mantenimiento.html')


# ============================================================
# EMOCIONES Y DASHBOARD
# ============================================================
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


# ============================================================
# PROCESAR EMOCIÓN (CÁMARA)
# ============================================================
@login_required
def procesar_emocion_camara(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id, usuario=request.user)
    data = json.loads(request.body)

    emocion_dominante = data.get("emocion", "Neutral")
    porcentaje = data.get("porcentaje", 0.0)
    emocion_obj = Emocion.objects.filter(nombre_emocion__iexact=emocion_dominante).first()

    if emocion_obj:
        EmocionReal.objects.create(
            sesion=sesion,
            emocion=emocion_obj,
            tipo_emocion=emocion_dominante,
            porcentaje=round(porcentaje, 2)
        )

 
    return redirect("mostrar_actividades", emocion_nombre=emocion_dominante)



# ============================================================
# PROCESAR EMOCIÓN (EMOTICONES MANUALES)
# ============================================================
@login_required
def registrar_emocion_manual(request):
    if request.method == 'POST':
        emocion_nombre = request.POST.get('emocion_nombre')
        porcentaje = float(request.POST.get('porcentaje', 0))
        emocion = get_object_or_404(Emocion, nombre_emocion__iexact=emocion_nombre)

        sesion = Sesion.objects.filter(usuario=request.user, activa=True).order_by('-fecha_inicio').first()
        if not sesion:
            sesion = Sesion.objects.create(usuario=request.user, activa=True)

        emocion_real, _ = EmocionReal.objects.get_or_create(
            sesion=sesion,
            emocion=emocion,
            tipo_emocion=emocion.nombre_emocion,
            defaults={'porcentaje': porcentaje}
        )
        emocion_real.porcentaje = porcentaje
        emocion_real.save()

        
        return redirect('mostrar_actividades', emocion_nombre=emocion.nombre_emocion)

    return redirect('extra')





@login_required
def seleccionar_emocion(request, emocion_nombre):
    """Versión simple sin porcentaje (en desuso si usas el slider)."""
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=emocion_nombre)
    sesion, _ = Sesion.objects.get_or_create(usuario=request.user, fecha_fin__isnull=True)
    EmocionReal.objects.create(sesion=sesion, emocion=emocion, tipo_emocion=emocion.nombre_emocion)
    return redirect('mostrar_actividades', emocion_nombre=emocion.nombre_emocion)


# ============================================================
# MOSTRAR ACTIVIDADES
# ============================================================
@login_required
def mostrar_actividades(request, emocion_nombre):
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=emocion_nombre)
    
    actividades_principal = list(Actividad.objects.filter(emocion=emocion))
    otras_actividades = list(Actividad.objects.exclude(emocion=emocion))
    otras_actividades = sample(otras_actividades, min(2, len(otras_actividades)))
    
    recomendaciones = []

    for act in actividades_principal:
        recomendaciones.append({'actividad': act, 'porcentaje': randint(80, 100)})
    
    for act in otras_actividades:
        recomendaciones.append({'actividad': act, 'porcentaje': randint(30, 50)})

    recomendaciones.sort(key=lambda x: x['porcentaje'], reverse=True)
    max_porcentaje = max([rec['porcentaje'] for rec in recomendaciones]) if recomendaciones else 0

    return render(request, 'actividades.html', {
        'emocion': emocion,
        'recomendaciones': recomendaciones,
        'max_porcentaje': max_porcentaje,
    })


# ============================================================
# PREDICCIÓN DE EMOCIONES (FASTAPI)
# ============================================================
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


# ============================================================
# ENCUESTA DE SATISFACCIÓN
# ============================================================
from django.contrib import messages
from .models import EncuestaSatisfaccion

@login_required
def encuesta_satisfaccion(request):
    sesion = Sesion.objects.filter(usuario=request.user).order_by('-fecha_inicio').first()

    if request.method == 'POST':
        utilidad = request.POST.get('utilidad')
        recomendacion = request.POST.get('recomendacion')
        comentario = request.POST.get('comentario', '')

        if utilidad and recomendacion:
            encuesta = EncuestaSatisfaccion.objects.create(
                sesion=sesion,  # 🔗 se asocia a la sesión actual o más reciente
                utilidad=utilidad,
                recomendacion=int(recomendacion),
                comentario=comentario
            )

            # Cerrar la sesión si aún está activa
            if sesion and sesion.activa:
                sesion.cerrar()

            return redirect('opciones')

    return render(request, 'encuesta_satisfaccion.html', {'sesion': sesion})



@login_required
def procesar_encuesta(request):
    if request.method == "POST":
        # Aquí procesas las respuestas de la encuesta
        respuestas = request.POST

@login_required(login_url='login')
def camara(request):
    sesion = Sesion.objects.filter(usuario=request.user, fecha_fin__isnull=True).first()
    if not sesion:
        sesion = Sesion.objects.create(usuario=request.user)
    return render(request, "camara.html", {"sesion_id": sesion.id})



def agenda_view(request):
    return render(request, 'agenda.html')

def actividades(request):
    return render(request, 'actividades.html')

def mantenimiento(request):
    return render(request, 'mantenimiento.html')

# ------------------------------
# ALUMNOS / ESCUELAS / DETALLES
# ------------------------------
def alumnos(request):
    usuarios = Usuario.objects.all()
    return render(request, 'modulo/alumnos.html', {'usuarios': usuarios})

def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})

def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Usuario, id=alumno_id)
    return render(request, 'modulo/detalle_alumno.html', {'alumno': alumno})

def escuelas(request):
    escuelas_sim = [
        {'id': 1, 'nombre': 'Informática y Telecomunicación', 'carreras': ['Programación', 'Redes'], 'sede': 'Melipilla'},
        {'id': 2, 'nombre': 'Construcción', 'carreras': ['Edificación', 'Arquitectura'], 'sede': 'Melipilla'},
        {'id': 3, 'nombre': 'Gastronomía', 'carreras': ['Cocina Profesional', 'Pastelería'], 'sede': 'Melipilla'},
        {'id': 4, 'nombre': 'Otra Escuela', 'carreras': ['Diseño', 'Administración'], 'sede': 'Melipilla'},
    ]
    return render(request, 'modulo/escuela.html', {'escuelas': escuelas_sim})

# ------------------------------
# SEGUIMIENTO / DASHBOARD
# ------------------------------
def seguimiento(request):
    emociones_agg = EmocionCamara.objects.values('nombre_emocion').annotate(cantidad=Count('id'))
    emociones = list(emociones_agg)

    datos_usuarios = []
    for u in Usuario.objects.all():
        sesiones = Sesion.objects.filter(usuario=u)
        emociones_usuario = EmocionCamara.objects.filter(sesion__in=sesiones)
        emociones_count = emociones_usuario.values('nombre_emocion').annotate(cantidad=Count('id'))
        datos_usuarios.append({'usuario': u.username, 'emociones': list(emociones_count)})

    return render(request, 'seguimiento.html', {'emociones': emociones, 'datos_usuarios': datos_usuarios})

def dashboard_emociones(request):
    datos = EmocionReal.objects.values('tipo_emocion').annotate(total=Count('id'))
    etiquetas = [d['tipo_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'dashboard_emociones.html', {'emociones_labels': etiquetas, 'emociones_counts': valores})

# ------------------------------
# MÓDULO PROFESOR (Dashboard)
# ------------------------------
def opciones(request):
    return render(request, 'opciones.html')

@login_required(login_url='login')
def modulo_profesor(request):
    return render(request, "modulo_profesor.html")

def grafico_profesor(request):
    profesor = request.user
    if getattr(profesor, "escuela", None):
        escuelas = [profesor.escuela]
    else:
        escuelas = Escuela.objects.all()

    datos_emociones, datos_duracion, datos_satisfaccion = [], [], []
    tipos_emocion = ['Alegría', 'Tristeza', 'Neutral', 'Miedo', 'Enojo', 'Sorpresa']

    for escuela in escuelas:
        sesiones_escuela = Sesion.objects.filter(usuario__escuela=escuela)
        emociones_reales = EmocionReal.objects.filter(sesion__in=sesiones_escuela)

        emociones_agregadas = {}
        emociones_porcentaje = {}
        for tipo in tipos_emocion:
            cantidad = emociones_reales.filter(tipo_emocion=tipo).count()
            emociones_agregadas[tipo.lower()] = cantidad
            emociones_porcentaje[tipo.lower()] = cantidad

        # Convertir a porcentaje
        total_escuela = sum(emociones_porcentaje.values())
        if total_escuela > 0:
            for tipo, cantidad in emociones_porcentaje.items():
                emociones_porcentaje[tipo] = round((cantidad / total_escuela) * 100, 2)
        else:
            emociones_porcentaje = {tipo.lower(): 0.0 for tipo in tipos_emocion}

        datos_emociones.append({
            "escuela": escuela.nombre,
            "cantidades": emociones_agregadas,
            "porcentajes": emociones_porcentaje
        })

        # Duración promedio sesiones
        sesiones_con_duracion = sesiones_escuela.filter(fecha_inicio__isnull=False, fecha_fin__isnull=False).annotate(
            dur_total=F('fecha_fin') - F('fecha_inicio')
        )
        dur_promedio_timedelta = sesiones_con_duracion.aggregate(promedio=Avg('dur_total'))['promedio']
        dur_prom_segundos = dur_promedio_timedelta.total_seconds() if dur_promedio_timedelta else 0
        datos_duracion.append({"escuela": escuela.nombre, "promedio": round(dur_prom_segundos, 2)})

        # Encuestas
        respuestas = RespuestaEncuesta.objects.filter(usuario__escuela=escuela)
        gusto = respuestas.filter(respuesta__icontains="si").count()
        no_gusto = respuestas.filter(respuesta__icontains="no").count()
        datos_satisfaccion.append({"escuela": escuela.nombre, "si": gusto, "no": no_gusto})

    # Totales globales
    emociones_globales = {}
    emociones_reales_globales = EmocionReal.objects.all()
    for tipo in tipos_emocion:
        cantidad_global = emociones_reales_globales.filter(tipo_emocion=tipo).count()
        emociones_globales[tipo.lower()] = cantidad_global

    total_global = sum(emociones_globales.values())
    if total_global > 0:
        for tipo, cantidad in emociones_globales.items():
            emociones_globales[tipo] = round((cantidad / total_global) * 100, 2)
    else:
        emociones_globales = {tipo.lower(): 0.0 for tipo in tipos_emocion}

    context = {
        "datos_emociones": json.dumps(datos_emociones),
        "datos_duracion": json.dumps(datos_duracion),
        "datos_satisfaccion": json.dumps(datos_satisfaccion),
        "emociones_globales": json.dumps(emociones_globales),
    }
    return render(request, "grafico_profesor.html", context)

# ------------------------------
# API / REGISTRO DE EMOCIONES
# ------------------------------
@csrf_exempt
@require_POST
def registrar_emocion(request):
    try:
        data = json.loads(request.body)
        sesion_id = data.get("sesion_id")
        nombre_emocion = data.get("nombre_emocion")
        probabilidad = data.get("probabilidad")
        duracion = data.get("duracion")
        fiabilidad = data.get("fiabilidad")

        sesion = Sesion.objects.get(id=sesion_id)
        emocion = EmocionCamara.objects.create(
            sesion=sesion,
            nombre_emocion=nombre_emocion,
            probabilidad=probabilidad,
            duracion=duracion,
            fiabilidad=fiabilidad
        )
        return JsonResponse({"status": "ok", "id": emocion.id, "mensaje": f"Emoción {nombre_emocion} guardada"})
    except Sesion.DoesNotExist:
        return JsonResponse({"status": "error", "mensaje": "Sesión no encontrada"}, status=404)
    except Exception as e:
        logger.exception("Error registrando emoción: %s", e)
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
def predict_emotion_view(request):
    if request.method != "POST":
        return JsonResponse({"label": "Null", "confidence": 0, "error": "Método no permitido"}, status=405)
    try:
        data = json.loads(request.body)
        image_base64 = data.get("image")
        if not image_base64:
            return JsonResponse({"label": "Null", "confidence": 0, "error": "No se proporcionó imagen"}, status=400)
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)
        Image.open(BytesIO(image_bytes))  # Validar imagen
        API_URL = "http://127.0.0.1:5000/predict_emotion"
        response = requests.post(API_URL, json={"image": image_base64}, timeout=5)
        result = response.json()
        return JsonResponse({
            "label": result.get("label", "Sin reconocer"),
            "confidence": result.get("confidence", 0)
        })
    except Exception as e:
        logger.exception("Error prediciendo emoción: %s", e)
        return JsonResponse({"label": "Null", "confidence": 0, "error": str(e)}, status=500)

# ------------------------------
# API AUXILIAR: EMOCIONES
# ------------------------------
def emociones_data(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nombre_emocion, COUNT(*) as total
                FROM gestion_emocion
                GROUP BY nombre_emocion;
            """)
            rows = cursor.fetchall()
        data = {"labels": [r[0] for r in rows], "values": [r[1] for r in rows]}
        return JsonResponse(data)
    except Exception as e:
        logger.exception("Error obteniendo emociones: %s", e)
        return JsonResponse({"labels": [], "values": [], "error": str(e)}, status=500)
# En views.py
@login_required
def finalizar_y_encuesta(request):
    """Finaliza la sesión activa del usuario y redirige a la encuesta."""
    sesion = Sesion.objects.filter(usuario=request.user, activa=True).order_by('-fecha_inicio').first()
    if sesion:
        sesion.cerrar()  # registra fecha_fin y pone activa=False
    return redirect('encuesta_satisfaccion')
def preguntas(request):
    return render(request, 'preguntas.html')


def mostrar_resultado(request):
    emocion = request.GET.get('emocion', 'Neutral')
    return render(request, "resultado.html", {"emocion": emocion})

def resultado(request):
    # Obtener emoción de query param
    nombre_emocion = request.GET.get("emocion", "Neutral")

    # Buscar la emoción
    emocion = get_object_or_404(Emocion, nombre_emocion__iexact=nombre_emocion)

    # Filtrar actividades según emoción
    actividades = Actividad.objects.filter(emocion=emocion)

    # Crear recomendaciones ficticias
    recomendaciones = [
        {"actividad": act, "porcentaje": 100}  # Aquí puedes calcular porcentaje real si quieres
        for act in actividades
    ]

    contexto = {
        "emocion": emocion,
        "recomendaciones": recomendaciones,
        "max_porcentaje": 100,
    }

    return render(request, "resultado.html", contexto)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def cerrar_sesion_ajax(request):
    """Cierra la sesión activa del usuario desde el navegador (por ejemplo, al cerrar pestaña)."""
    sesion = Sesion.objects.filter(usuario=request.user, activa=True).order_by('-fecha_inicio').first()
    if sesion:
        sesion.cerrar()
        return JsonResponse({"status": "ok", "message": "Sesión finalizada"})
    return JsonResponse({"status": "no_active_session"})

######################################
###### Actividade panel admin    #####
######################################

from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def admin_actividades(request):
    query = request.GET.get('q', '')  # Búsqueda por texto
    filtro_emocion = request.GET.get('emocion', '')  # Filtro por emoción

    actividades = Actividad.objects.select_related("emocion").all()

    # Aplicar filtro global
    if query:
        actividades = actividades.filter(
            Q(nombre_actividad__icontains=query) |
            Q(emocion__nombre_emocion__icontains=query)
        )

    if filtro_emocion:
        actividades = actividades.filter(emocion__nombre_emocion=filtro_emocion)

    # Paginación
    paginator = Paginator(actividades.order_by('id'), 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    emociones = Emocion.objects.all()

    return render(request, "admin_actividades.html", {
        "actividades": page_obj,
        "emociones": emociones,
        "query": query,
        "filtro_emocion": filtro_emocion,
    })


@login_required
def editar_actividad(request, id):
    actividad = Actividad.objects.get(id=id)

    if request.method == 'POST':
        actividad.nombre_actividad = request.POST['nombre_actividad']
        actividad.descripcion = request.POST['descripcion']
        actividad.emocion_id = request.POST['emocion_id']
        actividad.como_realizarla = request.POST['como_realizarla']
        actividad.importancia = request.POST['importancia']
        actividad.recurso = request.POST['recurso']
        actividad.save()

        return redirect('actividadesconf')

    emociones = Emocion.objects.all()
    return render(request, 'actividades/editar_actividad.html', {
        'actividad': actividad,
        'emociones': emociones
    })

@login_required
def eliminar_actividad(request, id):
    actividad = get_object_or_404(Actividad, id=id)
    actividad.delete()
    return redirect('actividadesconf')

@login_required
def crear_actividad(request):
    emociones = Emocion.objects.all()

    if request.method == "POST":
        nombre = request.POST.get("nombre_actividad")
        descripcion = request.POST.get("descripcion")
        emocion_id = request.POST.get("emocion_id")
        como = request.POST.get("como_realizarla")
        importancia = request.POST.get("importancia")
        recurso = request.POST.get("recurso")

        Actividad.objects.create(
            nombre_actividad=nombre,
            descripcion=descripcion,
            emocion_id=emocion_id,
            como_realizarla=como,
            importancia=importancia,
            recurso=recurso
        )

        return redirect("actividadesconf")

    return render(request, "actividades/crear_actividad.html", {"emociones": emociones})
