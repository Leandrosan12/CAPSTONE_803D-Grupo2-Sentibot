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
from .models import EncuestaSatisfaccion

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
    Sesion, Escuela
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

        # Asignar escuela
        if email.lower().endswith('@duoc.cl') or email.lower().endswith('@profesor.duoc.cl'):
            try:
                colaboradores = Escuela.objects.get(nombre='Colaboradores')
                user.escuela = colaboradores
            except Escuela.DoesNotExist:
                # Si no existe, no asignar o manejar error
                pass
        else:
            if escuela_id:
                try:
                    escuela = Escuela.objects.get(id=escuela_id)
                    user.escuela = escuela
                except Escuela.DoesNotExist:
                    pass

        user.save()

        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)

        return redirect('login')

    return render(request, 'registro.html', {'escuelas': Escuela.objects.all()})

# ------------------------------
# MÓDULOS PRINCIPALES
# ------------------------------
def modulo(request):
    return render(request, 'modulo/modulo.html')
 
from django.shortcuts import render
from .models import Escuela
@login_required(login_url='login')
def modulo_profesor(request):
    """Muestra la lista de escuelas en el módulo del profesor."""
    user_email = request.user.email.lower()
    if user_email.endswith('@duoc.cl') or user_email.endswith('@profesor.duoc.cl'):
        escuelas = Escuela.objects.filter(nombre='Colaboradores').order_by('nombre')
    else:
        escuelas = Escuela.objects.exclude(nombre='Colaboradores').order_by('nombre')
    return render(request, 'modulo_profesor.html', {'escuelas': escuelas})



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
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import Usuario, Escuela

def alumnos(request):
    # Obtener parámetro de búsqueda
    q = request.GET.get('q', '')  # Buscador general

    # Filtrado multicampo
    usuarios_lista = Usuario.objects.all().order_by('id')
    if q:
        usuarios_lista = usuarios_lista.filter(
            Q(id__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(escuela__nombre__icontains=q)
        )

    # PAGINACIÓN
    paginator = Paginator(usuarios_lista, 10)  # 10 usuarios por página
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    # Listar escuelas para el modal de añadir usuario
    if request.user.is_authenticated and (request.user.email.lower().endswith('@duoc.cl') or request.user.email.lower().endswith('@profesor.duoc.cl')):
        escuelas = Escuela.objects.filter(nombre='Colaboradores')
    else:
        escuelas = Escuela.objects.exclude(nombre='Colaboradores')

    return render(request, 'modulo/alumnos.html', {
        "usuarios": usuarios,
        "q": q,
        "escuelas": escuelas,
    })



from django.shortcuts import redirect
from gestion.models import Usuario, Escuela

def añadir_alumno(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        escuela_id = request.POST.get("escuela_id")

        escuela = Escuela.objects.get(id=escuela_id) if escuela_id else None

        # Crear usuario con username único (ej: igual al email)
        usuario = Usuario(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            escuela=escuela
        )
        usuario.set_password(password)
        usuario.save()

        return redirect('alumnos')



# from django.shortcuts import render, get_object_or_404
# from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
# from .models import Usuario, Sesion, EmocionReal, EncuestaSatisfaccion
# import json

# def detalle_alumno(request, alumno_id):
#     alumno = get_object_or_404(Usuario, id=alumno_id)

#     # --- EMOCIONES TOTALES ---
#     emociones_qs = EmocionReal.objects.filter(sesion__usuario=alumno)
#     emociones_data = {
#         "Feliz": emociones_qs.filter(tipo_emocion__iexact="Alegría").count(),
#         "Triste": emociones_qs.filter(tipo_emocion__iexact="Tristeza").count(),
#         "Miedo": emociones_qs.filter(tipo_emocion__iexact="Miedo").count(),
#         "Enojado": emociones_qs.filter(tipo_emocion__iexact="Enojo").count(),
#         "Neutral": emociones_qs.filter(tipo_emocion__iexact="Neutral").count(),
#     }

#     # --- TIEMPO PROMEDIO ---
#     duracion_expr = ExpressionWrapper(F('fecha_fin') - F('fecha_inicio'), output_field=DurationField())
#     sesiones = Sesion.objects.filter(usuario=alumno).annotate(duracion=duracion_expr)
#     promedio = sesiones.aggregate(promedio=Avg('duracion'))['promedio']
#     tiempo_promedio = promedio.total_seconds()/60 if promedio else 0

#     # --- ENCUESTAS DE TODAS LAS SESIONES ---
#     encuestas = EncuestaSatisfaccion.objects.filter(sesion__usuario=alumno)

#     # --- UTILIDAD ---
#     utilidad_count = {"Sí": 0, "No": 0}
#     for encuesta in encuestas:
#         if encuesta.utilidad == "1":  # <-- comparar como string
#             utilidad_count["Sí"] += 1
#         else:
#             utilidad_count["No"] += 1

#     # --- RECOMENDACIÓN ---
#     recomend_count = {str(i): 0 for i in range(1, 6)}
#     for encuesta in encuestas:
#         if encuesta.recomendacion:
#             key = str(encuesta.recomendacion)
#             if key in recomend_count:
#                 recomend_count[key] += 1

#     context = {
#         "alumno": alumno,
#         "emociones_json": json.dumps(emociones_data),
#         "tiempo_promedio": tiempo_promedio,
#         "utilidad_json": json.dumps(utilidad_count),
#         "recomend_json": json.dumps(recomend_count),
#     }

#     return render(request, "modulo/detalle_alumno.html", context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from .models import Usuario, Sesion, EmocionReal, EncuestaSatisfaccion
import json

def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Usuario, id=alumno_id)

    # --- EMOCIONES TOTALES ---
    emociones_qs = EmocionReal.objects.filter(sesion__usuario=alumno)
    emociones_data = {
        "Feliz": emociones_qs.filter(tipo_emocion__iexact="Alegría").count(),
        "Triste": emociones_qs.filter(tipo_emocion__iexact="Tristeza").count(),
        "Miedo": emociones_qs.filter(tipo_emocion__iexact="Miedo").count(),
        "Enojado": emociones_qs.filter(tipo_emocion__iexact="Enojo").count(),
        "Neutral": emociones_qs.filter(tipo_emocion__iexact="Neutral").count(),
    }

    # --- TIEMPO PROMEDIO ---
    duracion_expr = ExpressionWrapper(F('fecha_fin') - F('fecha_inicio'), output_field=DurationField())
    sesiones = Sesion.objects.filter(usuario=alumno).annotate(duracion=duracion_expr)
    promedio = sesiones.aggregate(promedio=Avg('duracion'))['promedio']
    tiempo_promedio = promedio.total_seconds()/60 if promedio else 0

    # --- UTILIDAD TOTAL ---
    utilidad_agg = EncuestaSatisfaccion.objects.filter(
        sesion__usuario=alumno
    ).aggregate(
        si=Count('id', filter=Q(utilidad='1')),
        no=Count('id', filter=Q(utilidad='0'))
    )
    utilidad_count = {
        "Sí": utilidad_agg.get('si', 0),
        "No": utilidad_agg.get('no', 0)
    }

    # --- RECOMENDACIÓN TOTAL ---
    recomend_agg = EncuestaSatisfaccion.objects.filter(
        sesion__usuario=alumno
    ).values('recomendacion').annotate(cantidad=Count('id'))

    recomend_count = {str(i): 0 for i in range(1, 6)}
    for r in recomend_agg:
        key = str(r['recomendacion'])
        if key in recomend_count:
            recomend_count[key] = r['cantidad']

    context = {
        "alumno": alumno,
        "emociones_json": json.dumps(emociones_data),
        "tiempo_promedio": tiempo_promedio,
        "utilidad_json": json.dumps(utilidad_count),
        "recomend_json": json.dumps(recomend_count),
    }

    return render(request, "modulo/detalle_alumno.html", context)





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
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def eliminar_alumno(request, alumno_id):
    if request.method == "POST":
        alumno = get_object_or_404(Usuario, id=alumno_id)
        alumno.delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

@csrf_exempt
def actualizar_alumno(request, alumno_id):
    if request.method == "POST":
        alumno = get_object_or_404(Usuario, id=alumno_id)
        data = json.loads(request.body)

        alumno.first_name = data.get('nombre', alumno.first_name)
        alumno.last_name = data.get('apellido', alumno.last_name)
        alumno.email = data.get('email', alumno.email)

        escuela_id = data.get('escuela')
        rol_id = data.get('rol')

        if escuela_id:
            alumno.escuela_id = escuela_id
        if rol_id:
            alumno.rol_id = rol_id

        alumno.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)




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


def mantenimiento(request):
    return render(request, 'mantenimiento.html')

# ------------------------------
# ALUMNOS / ESCUELAS / DETALLES
# ------------------------------

def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})



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

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from collections import Counter
from .models import Escuela, Sesion, EmocionReal, EncuestaSatisfaccion
from django.contrib.auth.decorators import login_required


@login_required
def grafico_profesor(request, escuela_id):
    escuela = get_object_or_404(Escuela, id=escuela_id)

    # --- Emociones por escuela ---
    emociones_raw = EmocionReal.objects.filter(
        sesion__usuario__escuela=escuela
    ).values('tipo_emocion').annotate(total=Count('id'))
    emociones_por_escuela = {e['tipo_emocion']: e['total'] for e in emociones_raw}

    # --- Emociones global ---
    emociones_global_raw = EmocionReal.objects.values('tipo_emocion').annotate(total=Count('id'))
    emociones_global = {e['tipo_emocion']: e['total'] for e in emociones_global_raw}

    # --- Duración de sesiones ---
    duracion = ExpressionWrapper(F('fecha_fin') - F('fecha_inicio'), output_field=DurationField())

    # --- Tiempo promedio por escuela seleccionada ---
    sesiones_escuela = Sesion.objects.filter(usuario__escuela=escuela).annotate(duracion=duracion)
    promedio_min_escuela = sesiones_escuela.aggregate(promedio=Avg('duracion'))['promedio']
    tiempo_promedio_escuela = promedio_min_escuela.total_seconds()/60 if promedio_min_escuela else 0

    # --- Tiempo promedio global ---
    sesiones_global = Sesion.objects.all().annotate(duracion=duracion)
    promedio_min_global = sesiones_global.aggregate(promedio=Avg('duracion'))['promedio']
    tiempo_promedio_global = promedio_min_global.total_seconds()/60 if promedio_min_global else 0

    # --- Promedios por todas las escuelas ---
    promedios_escuelas = {}
    for e in Escuela.objects.all():
        sesiones_e = Sesion.objects.filter(usuario__escuela=e).annotate(duracion=duracion)
        promedio = sesiones_e.aggregate(promedio=Avg('duracion'))['promedio']
        promedios_escuelas[e.nombre] = promedio.total_seconds()/60 if promedio else 0

    # --- Sesiones totales ---
    sesiones_totales_escuela = sesiones_escuela.count()
    sesiones_totales_global = sesiones_global.count()

    # --- Emociones positivas vs negativas ---
    positivas = ['Alegría', 'Neutral']
    negativas = ['Enojo', 'Tristeza', 'Miedo']

    emoc_positivas_escuela = EmocionReal.objects.filter(
        sesion__usuario__escuela=escuela, tipo_emocion__in=positivas
    ).count()
    emoc_negativas_escuela = EmocionReal.objects.filter(
        sesion__usuario__escuela=escuela, tipo_emocion__in=negativas
    ).count()

    emoc_positivas_global = EmocionReal.objects.filter(tipo_emocion__in=positivas).count()
    emoc_negativas_global = EmocionReal.objects.filter(tipo_emocion__in=negativas).count()

    # --- Encuesta de satisfacción ---
    encuestas_escuela = EncuestaSatisfaccion.objects.filter(sesion__usuario__escuela=escuela)

    # --- Gráfico barras: Recomendación 1-5 ---
    recomendaciones = [e.recomendacion for e in encuestas_escuela if e.recomendacion]
    recomendaciones_count = Counter(recomendaciones)
    satisfaccion_barras = {i: recomendaciones_count.get(i, 0) for i in range(1, 6)}

    # --- Gráfico torta: Utilidad Sí/No (solo escuela actual) ---
    utilidad_escuela_list = [
        'Sí' if str(e.utilidad) == "1" else 'No'
        for e in encuestas_escuela
    ]
    utilidad_count_escuela = Counter(utilidad_escuela_list)

    utilidad_escuela = {
        'Sí': utilidad_count_escuela.get('Sí', 0),
        'No': utilidad_count_escuela.get('No', 0),
    }

    # --- Encuestas globales ---
    encuestas_global = EncuestaSatisfaccion.objects.filter(sesion__usuario__escuela__isnull=False)
    recomendaciones_global = {}
    satisfaccion_torta_global = {}
    utilidad_global = {}

    for e in Escuela.objects.all():
        enc = encuestas_global.filter(sesion__usuario__escuela=e)

        # Recomendaciones 1 a 5
        count_rec = Counter([i.recomendacion for i in enc if i.recomendacion])
        recomendaciones_global[e.nombre] = {i: count_rec.get(i, 0) for i in range(1, 6)}

        # Utilidad sí/no
        count_utilidad = Counter([
            'Sí' if str(i.utilidad) == "1" else 'No'
            for i in enc
        ])
        utilidad_global[e.nombre] = {
            'Sí': count_utilidad.get('Sí', 0),
            'No': count_utilidad.get('No', 0),
        }

        # Para compatibilidad con tu template previo
        satisfaccion_torta_global[e.nombre] = utilidad_global[e.nombre]

    context = {
        "escuela": escuela,
        "emociones_por_escuela": emociones_por_escuela,
        "emociones_global": emociones_global,
        "tiempo_promedio": round(tiempo_promedio_escuela, 2),
        "tiempo_promedio_global": round(tiempo_promedio_global, 2),
        "sesiones_totales_escuela": sesiones_totales_escuela,
        "sesiones_totales_global": sesiones_totales_global,
        "emoc_positivas_escuela": emoc_positivas_escuela,
        "emoc_negativas_escuela": emoc_negativas_escuela,
        "emoc_positivas_global": emoc_positivas_global,
        "emoc_negativas_global": emoc_negativas_global,
        "promedios_escuelas": promedios_escuelas,

        # Satisfacción escuela actual
        "satisfaccion_barras": satisfaccion_barras,
        "satisfaccion_torta": utilidad_escuela,
        "utilidad_escuela": utilidad_escuela,

        # Satisfacción global por escuela
        "satisfaccion_barras_global": recomendaciones_global,
        "satisfaccion_torta_global": satisfaccion_torta_global,
        "utilidad_global": utilidad_global,
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

from django.shortcuts import render
from .models import Escuela

def escuelas(request):
    if request.user.is_authenticated and (request.user.email.lower().endswith('@duoc.cl') or request.user.email.lower().endswith('@profesor.duoc.cl')):
        lista = Escuela.objects.filter(nombre='Colaboradores')
    else:
        lista = Escuela.objects.exclude(nombre='Colaboradores')
    return render(request, "escuelas.html", {"escuelas": lista})

from django.http import HttpResponse
from reportlab.pdfgen import canvas

def descargar_reporte(request, escuela_id):
    # Crear respuesta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_escuela_{escuela_id}.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 750, f"Reporte de Escuela ID {escuela_id}")
    p.drawString(100, 730, "Aquí va tu resumen real…")
    p.showPage()
    p.save()

    return response

from django.db.models import Count
from django.http import JsonResponse
from .models import EmocionReal


def emociones_por_escuela(request):
    # Obtiene un conteo de emociones por Escuela
    data = (
        EmocionReal.objects
        .values(
            "sesion__usuario__escuela__nombre",     # Escuela
            "emocion__nombre_emocion"              # Emoción de la BD
        )
        .annotate(total=Count("id"))               # Cuenta cuántas veces aparece
        .order_by("sesion__usuario__escuela__nombre")
    )
    result = {}
    for item in data:
        escuela = item["sesion__usuario__escuela__nombre"]
        emocion = item["emocion__nombre_emocion"]
        total = item["total"]

        if escuela not in result:
            result[escuela] = {}

        result[escuela][emocion] = total

    return JsonResponse(result)


from django.db.models import Avg, ExpressionWrapper, F, DurationField
from django.shortcuts import render, get_object_or_404
from .models import Sesion, Escuela

def tiempo_promedio_sesion_por_escuela(request, escuela_id):
    escuela = get_object_or_404(Escuela, id=escuela_id)

    # Cálculo correcto de duración usando fecha_inicio y fecha_fin
    duracion = ExpressionWrapper(
        F('fecha_fin') - F('fecha_inicio'),
        output_field=DurationField()
    )

    # Filtrar sesiones por escuela REAL del usuario
    sesiones = (
        Sesion.objects
        .filter(usuario__escuela_id=escuela_id)
        .annotate(duracion=duracion)
    )

    # Promedio
    promedio = sesiones.aggregate(promedio=Avg('duracion'))['promedio']

    # Convertimos a minutos
    promedio_min = promedio.total_seconds() / 60 if promedio else 0

    context = {
        "escuela": escuela,
        "promedio_min": round(promedio_min, 2)
    }

    return render(request, "dashboard/tiempo_promedio_sesion.html", context)

# Recuperar correo

from gestion.models import Usuario
import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail

codigos_reset = {}  # temporal

def recuperar_contrasena(request):
    if request.method == 'POST':
        correo = request.POST.get("correo")

        try:
            user = Usuario.objects.get(email=correo)
        except Usuario.DoesNotExist:
            return render(request, "recuperar_contrasena.html", {
                "mensaje": "El correo no está registrado."
            })

        # Generar código
        codigo = str(random.randint(100000, 999999))
        codigos_reset[correo] = codigo

        # Enviar correo
        send_mail(
            "Recuperación de contraseña",
            f"Tu código de recuperación es: {codigo}",
            "no-reply@miapp.com",
            [correo],
        )

        # Guardamos correo en la sesión para no recorrer dict más tarde
        request.session["correo_reset"] = correo

        return redirect("confirmar_contrasena")

    return render(request, "recuperar_contrasena.html")



def confirmar_contrasena(request):
    if request.method == 'POST':
        codigo = request.POST.get("codigo")
        nueva = request.POST.get("nueva_contrasena")

        correo = request.session.get("correo_reset")

        if not correo:
            return render(request, "confirmar_contrasena.html", {
                "mensaje": "El proceso expiró. Intenta nuevamente."
            })

        codigo_guardado = codigos_reset.get(correo)

        if codigo == codigo_guardado:
            try:
                user = Usuario.objects.get(email=correo)
                user.set_password(nueva)
                user.save()

                # Limpiar datos
                codigos_reset.pop(correo, None)
                del request.session["correo_reset"]

                # Redirigir al login después de cambiar la contraseña
                return redirect("login")   # <--- 🔥 AQUÍ VA AL LOGIN

            except Usuario.DoesNotExist:
                return render(request, "confirmar_contrasena.html", {
                    "mensaje": "No se encontró el usuario."
                })

        return render(request, "confirmar_contrasena.html", {
            "mensaje": "El código ingresado no es válido."
        })

    return render(request, "confirmar_contrasena.html")

from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, Escuela
from django.contrib import messages

def editar_alumno(request, alumno_id):
    usuario = get_object_or_404(Usuario, id=alumno_id)
    if request.user.is_authenticated and (request.user.email.lower().endswith('@duoc.cl') or request.user.email.lower().endswith('@profesor.duoc.cl')):
        escuelas = Escuela.objects.filter(nombre='Colaboradores')
    else:
        escuelas = Escuela.objects.exclude(nombre='Colaboradores')

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')
        usuario.escuela_id = request.POST.get('escuela')
        usuario.is_staff = 1 if request.POST.get('is_staff') == '1' else 0
        usuario.save()

        messages.success(request, "Los cambios se guardaron correctamente.")
        return redirect('alumnos')

    return render(request, 'modulo/editar_alumno.html', {
        'usuario': usuario,
        'escuelas': escuelas
    })






from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Usuario

def listar_alumnos(request):
    id_query = request.GET.get('id', '')

    if id_query:
        usuarios_lista = Usuario.objects.filter(id=id_query)
    else:
        usuarios_lista = Usuario.objects.all().order_by('id')

    # Paginar 10 por página
    paginator = Paginator(usuarios_lista, 10)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)  # Esto es clave

    return render(request, 'modulo/alumnos.html', {
        'usuarios': usuarios,
        'id': id_query
    })
from django.shortcuts import redirect, get_object_or_404
from gestion.models import Usuario

def eliminar_alumno(request, alumno_id):
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id=alumno_id)
        usuario.delete()
        return redirect('alumnos')  # redirige al listado



from django.shortcuts import redirect
from django.contrib import messages
from .models import Escuela

@login_required
def agregar_escuela(request):
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect(request.META.get("HTTP_REFERER", "modulo"))

    nombre = (request.POST.get("nombre") or "").strip()
    direccion = (request.POST.get("direccion") or "").strip()

    if not nombre:
        messages.error(request, "El nombre de la escuela es requerido.")
        return redirect(request.META.get("HTTP_REFERER", "modulo"))

    # Intenta crear con el campo direccion si existe; fallback si no existe
    try:
        # Si el modelo tiene el campo 'direccion', lo usamos.
        Escuela.objects.create(nombre=nombre, direccion=direccion)
    except TypeError:
        # Si el constructor no acepta 'direccion' (modelo antiguo), creamos solo con nombre
        Escuela.objects.create(nombre=nombre)

    messages.success(request, "Escuela creada correctamente.")
    return redirect(request.META.get("HTTP_REFERER", "modulo"))

from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import redirect
from .models import Escuela

def eliminar_escuela(request):
    if request.method == "POST":
        escuela_id = request.POST.get("escuela_id")
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        # Validar credenciales
        user = authenticate(request, username=correo, password=password)

        if user is None:
            messages.error(request, "Credenciales incorrectas")
            return redirect("modulo_profesor")

        # Buscar escuela y eliminarla
        try:
            escuela = Escuela.objects.get(id=escuela_id)
            escuela.delete()
            messages.success(request, "Escuela eliminada correctamente")
        except Escuela.DoesNotExist:
            messages.error(request, "La escuela no existe")

    return redirect("modulo_profesor")
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Escuela

def editar_escuela(request):
    if request.method == "POST":

        escuela_id = request.POST.get("escuela_id")
        nuevo_nombre = request.POST.get("nuevo_nombre")
        nueva_direccion = request.POST.get("nueva_direccion")

        escuela = get_object_or_404(Escuela, id=escuela_id)

        escuela.nombre = nuevo_nombre
        escuela.direccion = nueva_direccion
        escuela.save()

        messages.success(request, "✔️ La escuela ha sido actualizada correctamente.")
        return redirect("modulo_profesor")

    return redirect("modulo_profesor")
