# views.py limpio y funcional

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import connection
from .models import Sesion, EmocionCamara, Usuario
from gestion.models import Usuario as GestionUsuario, Emocion, EmocionReal, Sesion as GestionSesion

User = get_user_model()

# ------------------------------
# LOGIN / LOGOUT
# ------------------------------
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
# REGISTRO NORMAL
# ------------------------------
def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'Correo ya registrado'})

        # Generar username automático a partir del email
        username = email.split('@')[0]

        user = User.objects.create_user(
            username=username,   # ⚡ obligatorio para AbstractUser
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


def agenda_view(request):
    return render(request, 'agenda.html')


# ------------------------------
# MÓDULOS PRINCIPALES
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
def actividades(request):
    return render(request, 'actividades.html')
def lista_usuarios(request):
    # tu lógica aquí, por ejemplo:
    return render(request, 'lista_usuarios.html')


def mantenimiento(request):
    return render(request, 'mantenimiento.html')


# ------------------------------
# SEGUIMIENTO / EMOCIONES
# ------------------------------
def seguimiento(request):
    emociones = EmocionCamara.objects.values('nombre_emocion').annotate(cantidad=Count('id'))
    emociones = list(emociones)

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


def predict_emotion_view(request):
    # Mantengo la función tal como estaba
    pass


def dashboard_emociones(request):
    datos = EmocionReal.objects.values('emocion__nombre_emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion__nombre_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'dashboard_emociones.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })


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

