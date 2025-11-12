# Django shortcuts y utilidades
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
<<<<<<< HEAD
from django.db.models import Count
from django.db import connection
from .models import Usuario, Emocion, EmocionReal, Sesion
import json
import base64
from io import BytesIO
from PIL import Image
=======
from django.contrib.auth.decorators import login_required
from django.utils import timezone
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2

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

<<<<<<< HEAD

def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
=======
logger = logging.getLogger(__name__)
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2


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
# Páginas principales
# ------------------------------
def perfil(request):
    return render(request, 'perfil.html')


<<<<<<< HEAD
=======

@login_required(login_url='login')  # ajusta la URL si la llamas distinto
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2
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

<<<<<<< HEAD

# ------------------------------
# Módulos principales
# ------------------------------
=======
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2
def modulo(request):
    return render(request, 'modulo/modulo.html')


def modulo_profesor(request):
    return render(request, 'modulo_profesor.html')

from django.shortcuts import render
from .models import Usuario  # o el modelo que uses para usuarios

<<<<<<< HEAD

# ------------------------------
# Módulo Alumnos y Escuelas
# ------------------------------
=======
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2
def alumnos(request):
    usuarios = Usuario.objects.all()  # Trae todos los usuarios
    return render(request, 'modulo/alumnos.html', {'usuarios': usuarios})

<<<<<<< HEAD

def dashboard(request):
    return render(request, "dashboard.html")


def detalle_alumno(request, alumno_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario WHERE id = %s", [alumno_id])
        columnas = [col[0] for col in cursor.description]
        alumno = dict(zip(columnas, cursor.fetchone()))
    return render(request, 'detalle_alumno.html', {'alumno': alumno})
=======

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Usuario  # tu modelo personalizado

def detalle_alumno(request, id):
    alumno = get_object_or_404(Usuario, id=id)
    return render(request, 'modulo/detalle_alumno.html', {'alumno': alumno})
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2


def escuelas(request):
<<<<<<< HEAD
    escuelas = [
        {'id': 1, 'nombre': 'Informática y Telecomunicación', 'carreras': ['Programación', 'Redes'], 'sede': 'Melipilla'},
        {'id': 2, 'nombre': 'Construcción', 'carreras': ['Edificación', 'Arquitectura'], 'sede': 'Melipilla'},
        {'id': 3, 'nombre': 'Gastronomía', 'carreras': ['Cocina Profesional', 'Pastelería'], 'sede': 'Melipilla'},
        {'id': 4, 'nombre': 'Otra Escuela', 'carreras': ['Diseño', 'Administración'], 'sede': 'Melipilla'},
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


=======
    return render(request, 'modulo/escuelas.html')

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
# API de predicción de emociones
# ------------------------------
>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2
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

<<<<<<< HEAD

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
# Detalle de Escuela (simulación)
# ------------------------------
def detalle_escuela(request, nombre_escuela):
    """
    Simula los detalles de cada escuela.
    En el futuro, esto se conectará con la base de datos.
    """
    detalles = {
        "Informática y Telecomunicación": {
            "nombre": "Informática y Telecomunicación",
            "sede": "Melipilla",
            "director": "Juan Torres",
            "correo": "juan.torres@duocuc.cl",
            "telefono": "+569 87654321",
            "descripcion": "Escuela enfocada en formar profesionales en programación, redes y tecnologías emergentes."
        },
        "Construcción": {
            "nombre": "Construcción",
            "sede": "Melipilla",
            "director": "María Rojas",
            "correo": "maria.rojas@duocuc.cl",
            "telefono": "+569 91234567",
            "descripcion": "Escuela especializada en proyectos de edificación y obras civiles."
        },
        "Gastronomía": {
            "nombre": "Gastronomía",
            "sede": "Melipilla",
            "director": "Pedro López",
            "correo": "pedro.lopez@duocuc.cl",
            "telefono": "+569 99999999",
            "descripcion": "Formación profesional en cocina nacional e internacional."
        },
        "Otra Escuela": {
            "nombre": "Otra Escuela",
            "sede": "Melipilla",
            "director": "Ana Díaz",
            "correo": "ana.diaz@duocuc.cl",
            "telefono": "+569 88888888",
            "descripcion": "Centro académico con múltiples áreas de conocimiento."
        }
    }

    escuela = detalles.get(nombre_escuela, None)
    return render(request, "detalle_escuela.html", {"escuela": escuela})
=======

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import EmocionCamara, Sesion

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import EmocionCamara, Sesion

@csrf_exempt
@require_POST
def registrar_emocion(request):
    try:
        data = json.loads(request.body)
        print("Datos recibidos:", data)  # 🔹 Para ver qué llega desde JS

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
        print("Sesión no encontrada:", sesion_id)
        return JsonResponse({"status": "error", "mensaje": "Sesión no encontrada"}, status=404)
    except Exception as e:
        print("Error interno:", str(e))
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)


# gestion/views.py (reemplaza todo el contenido por esto)
import json
import logging
import secrets

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


def enviar_codigo(request):
    """
    Genera y envía un código de 6 dígitos al correo. Guarda en sesión la expiración
    como ISO de un datetime aware (si USE_TZ=True).
    """
    correo = request.GET.get('correo')  # en producción usar POST
    if not correo:
        return JsonResponse({'error': 'Correo requerido'}, status=400)

    # Generar código legible: 6 dígitos
    codigo = f"{secrets.randbelow(1000000):06d}"
    expiracion = timezone.now() + timezone.timedelta(minutes=10)

    # Guardar en sesión (expiracion como ISO de aware datetime)
    request.session['codigo_verificacion'] = codigo
    request.session['correo_verificacion'] = correo
    request.session['codigo_expira'] = expiracion.isoformat()
    request.session.save()  # forzar persistencia inmediata

    subject = 'Tu código de verificación'
    message = f'Hola,\n\nTu código de verificación es: {codigo}\n\nExpira en 10 minutos.'
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, from_email, [correo], fail_silently=False)
        logger.info("Código %s enviado a %s", codigo, correo)
        return JsonResponse({'mensaje': 'Código enviado al correo.'})
    except Exception as e:
        logger.exception("Error enviando correo a %s: %s", correo, e)
        # Limpiar sesión si falla el envío
        request.session.pop('codigo_verificacion', None)
        request.session.pop('correo_verificacion', None)
        request.session.pop('codigo_expira', None)
        return JsonResponse({'error': 'No se pudo enviar el correo. Revisa configuración de correo.'}, status=500)


@require_POST
def validar_codigo(request):
    """
    Espera JSON con { correo, codigo } y valida contra lo guardado en sesión.
    Responde {"ok": True} o {"ok": False, "error": "..."}
    """
    try:
        body_text = request.body.decode('utf-8')
    except Exception:
        body_text = '<no body>'

    # DEBUG: mostrar en consola
    print("DEBUG validar_codigo - request.body:", body_text)
    print("DEBUG validar_codigo - session keys:", list(request.session.keys()))
    print("DEBUG validar_codigo - session data:",
          {k: request.session.get(k) for k in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']})

    # parsear JSON
    try:
        payload = json.loads(body_text)
        correo = (payload.get('correo') or '').strip().lower()
        codigo = (payload.get('codigo') or '').strip()
    except Exception:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    codigo_sesion = request.session.get('codigo_verificacion')
    correo_sesion = (request.session.get('correo_verificacion') or '').lower()
    codigo_expira_iso = request.session.get('codigo_expira')

    if not (codigo_sesion and correo_sesion and codigo_expira_iso):
        return JsonResponse({"ok": False, "error": "No hay un código de verificación válido. Verifica tu correo."}, status=400)

    if correo != correo_sesion:
        return JsonResponse({"ok": False, "error": "El correo no coincide con el verificado."}, status=400)

    # parsear fecha y normalizar timezone
    try:
        expiracion = parse_datetime(codigo_expira_iso)
        if expiracion is None:
            raise ValueError(f"No se pudo parsear la fecha desde sesión: {codigo_expira_iso}")

        # si es naive -> convertir a aware usando tz del proyecto
        if timezone.is_naive(expiracion):
            expiracion = timezone.make_aware(expiracion, timezone.get_current_timezone())

        now = timezone.now()
        if timezone.is_naive(now):
            now = timezone.make_aware(now, timezone.get_current_timezone())

        print("DEBUG validar_codigo - expiracion tzinfo:", expiracion.tzinfo)
        print("DEBUG validar_codigo - now tzinfo:", now.tzinfo)
    except Exception as e:
        # limpiar sesión por seguridad
        request.session.pop('codigo_verificacion', None)
        request.session.pop('correo_verificacion', None)
        request.session.pop('codigo_expira', None)
        logger.exception("Error parseando fecha en validar_codigo: %s", e)
        return JsonResponse({"ok": False, "error": "Error en el proceso (fecha). Solicita nuevo código."}, status=400)

    # comprobar expiración
    if now > expiracion:
        request.session.pop('codigo_verificacion', None)
        request.session.pop('correo_verificacion', None)
        request.session.pop('codigo_expira', None)
        return JsonResponse({"ok": False, "error": "El código ha expirado. Solicita uno nuevo."}, status=400)

    if codigo != codigo_sesion:
        return JsonResponse({"ok": False, "error": "Código inválido."}, status=400)

    return JsonResponse({"ok": True})

from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from gestion.models import Escuela, Usuario  # ✅ usamos Usuario, no Perfil


def registro(request):
    if request.method == "POST":
        email = (request.POST.get('correo') or '').strip()
        password = request.POST.get('contrasena')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        codigo = (request.POST.get('codigo') or '').strip()
        escuela_id = request.POST.get('escuela')  # ✅ capturamos la escuela seleccionada

        # 🔹 Datos de sesión para verificación
        codigo_sesion = request.session.get('codigo_verificacion')
        correo_sesion = request.session.get('correo_verificacion')
        codigo_expira_iso = request.session.get('codigo_expira')

        # Validaciones básicas
        if not (codigo_sesion and correo_sesion and codigo_expira_iso):
            return render(request, 'registro.html', {
                'error': 'No hay un código de verificación válido. Verifica tu correo primero.',
                'escuelas': Escuela.objects.all()
            })

        if email.lower() != correo_sesion.lower():
            return render(request, 'registro.html', {
                'error': 'El correo no coincide con el que se verificó.',
                'escuelas': Escuela.objects.all()
            })

        # 🔹 Validar expiración del código
        try:
            expiracion = parse_datetime(codigo_expira_iso)
            if expiracion is None and isinstance(codigo_expira_iso, str):
                if codigo_expira_iso.endswith('Z'):
                    expiracion = parse_datetime(codigo_expira_iso[:-1] + '+00:00')
            if expiracion is None:
                raise ValueError("No se pudo parsear la fecha de expiración")

            if timezone.is_naive(expiracion):
                expiracion = timezone.make_aware(expiracion, timezone.get_current_timezone())

            now = timezone.now()
            if timezone.is_naive(now):
                now = timezone.make_aware(now, timezone.get_current_timezone())

        except Exception:
            for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
                request.session.pop(key, None)
            return render(request, 'registro.html', {
                'error': 'Error en el proceso de verificación. Solicita un nuevo código.',
                'escuelas': Escuela.objects.all()
            })

        if now > expiracion:
            for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
                request.session.pop(key, None)
            return render(request, 'registro.html', {
                'error': 'El código ha expirado. Solicita uno nuevo.',
                'escuelas': Escuela.objects.all()
            })

        if codigo != codigo_sesion:
            return render(request, 'registro.html', {
                'error': 'Código de verificación inválido.',
                'escuelas': Escuela.objects.all()
            })

        # 🔹 Verificar si el email ya existe
        if Usuario.objects.filter(email__iexact=email).exists():
            for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
                request.session.pop(key, None)
            return render(request, 'registro.html', {
                'error': 'El email ya está registrado',
                'escuelas': Escuela.objects.all()
            })

        # 🔹 Crear usuario
        user = Usuario.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=email
        )

        # 🔹 Asignar escuela elegida (o detectar automáticamente)
        escuela = None
        if escuela_id:
            try:
                escuela = Escuela.objects.get(id=escuela_id)
            except Escuela.DoesNotExist:
                pass

        if not escuela:  # Si no seleccionó, intentamos deducir por correo
            dominio = email.split('@')[-1].lower()
            if "admin" in dominio or "negocios" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Administración y Negocios").first()
            elif "comunicacion" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Comunicación").first()
            elif "construccion" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Construcción").first()
            elif "diseno" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Diseño").first()
            elif "gastronomia" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Gastronomía").first()
            elif "informatica" in email.lower() or "telecom" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Informática").first()
            elif "ingenieria" in email.lower() or "recursos" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Ingeniería").first()
            elif "salud" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Salud").first()
            elif "turismo" in email.lower() or "hospitalidad" in email.lower():
                escuela = Escuela.objects.filter(nombre__icontains="Turismo").first()

        if escuela:
            user.escuela = escuela
            user.save()

        # 🔹 Limpiar sesión
        for key in ['codigo_verificacion', 'correo_verificacion', 'codigo_expira']:
            request.session.pop(key, None)

        return redirect('login')

    # ✅ Cargar escuelas para el formulario GET
    escuelas = Escuela.objects.all()
    return render(request, 'registro.html', {'escuelas': escuelas})

>>>>>>> cd578bd98aff33d6b9ff70b0047d7be6d0f735a2
