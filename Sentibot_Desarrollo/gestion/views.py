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
# Páginas principales
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

def modulo(request):
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    return render(request, 'modulo_profesor.html')

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

def registro(request):
    if request.method == "POST":
        email = (request.POST.get('correo') or '').strip()
        password = request.POST.get('contrasena')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        codigo = (request.POST.get('codigo') or '').strip()

        codigo_sesion = request.session.get('codigo_verificacion')
        correo_sesion = request.session.get('correo_verificacion')
        codigo_expira_iso = request.session.get('codigo_expira')

        if not (codigo_sesion and correo_sesion and codigo_expira_iso):
            return render(request, 'registro.html', {'error': 'No hay un código de verificación válido. Verifica tu correo primero.'})

        if email.lower() != correo_sesion.lower():
            return render(request, 'registro.html', {'error': 'El correo no coincide con el que se verificó.'})

        try:
            expiracion = parse_datetime(codigo_expira_iso)
            if expiracion is None:
                s = codigo_expira_iso
                if isinstance(s, str) and s.endswith('Z'):
                    s = s[:-1] + '+00:00'
                    expiracion = parse_datetime(s)
            if expiracion is None:
                raise ValueError("No se pudo parsear la fecha de expiración")
            if timezone.is_naive(expiracion):
                expiracion = timezone.make_aware(expiracion, timezone.get_current_timezone())
            now = timezone.now()
            if timezone.is_naive(now):
                now = timezone.make_aware(now, timezone.get_current_timezone())
        except Exception as e:
            request.session.pop('codigo_verificacion', None)
            request.session.pop('correo_verificacion', None)
            request.session.pop('codigo_expira', None)
            return render(request, 'registro.html', {'error': 'Error en el proceso de verificación. Solicita un nuevo código.'})

        if now > expiracion:
            request.session.pop('codigo_verificacion', None)
            request.session.pop('correo_verificacion', None)
            request.session.pop('codigo_expira', None)
            return render(request, 'registro.html', {'error': 'El código ha expirado. Solicita uno nuevo.'})

        if codigo != codigo_sesion:
            return render(request, 'registro.html', {'error': 'Código de verificación inválido.'})

        try:
            exists = User.objects.filter(email__iexact=email).exists()
        except Exception:
            try:
                exists = User.objects.filter(**{User.USERNAME_FIELD + "__iexact": email}).exists()
            except Exception:
                exists = False

        if exists:
            request.session.pop('codigo_verificacion', None)
            request.session.pop('correo_verificacion', None)
            request.session.pop('codigo_expira', None)
            return render(request, 'registro.html', {'error': 'El email ya está registrado'})

        username_field = getattr(User, 'USERNAME_FIELD', 'username')
        create_kwargs = {}
        create_kwargs[username_field] = email
        field_names = [f.name for f in User._meta.get_fields() if hasattr(f, 'name')]
        if 'email' in field_names and username_field != 'email':
            create_kwargs['email'] = email
        if 'first_name' in field_names:
            create_kwargs['first_name'] = first_name
        if 'last_name' in field_names:
            create_kwargs['last_name'] = last_name

        user = None
        try:
            create_kwargs['password'] = password
            user = User.objects.create_user(**create_kwargs)
        except TypeError:
            try:
                pos_args = [create_kwargs.pop(username_field)]
                user = User.objects.create_user(*pos_args, password=password, **create_kwargs)
            except Exception as e:
                try:
                    manual_kwargs = {k: v for k, v in create_kwargs.items() if k in field_names}
                    manual_kwargs[username_field] = manual_kwargs.get(username_field, email)
                    user = User(**manual_kwargs)
                    user.set_password(password)
                    user.save()
                except Exception as e2:
                    request.session.pop('codigo_verificacion', None)
                    request.session.pop('correo_verificacion', None)
                    request.session.pop('codigo_expira', None)
                    return render(request, 'registro.html', {'error': 'No se pudo crear el usuario. Revisa la configuración del modelo de usuario.'})

        try:
            changed = False
            if first_name and getattr(user, 'first_name', None) != first_name:
                user.first_name = first_name
                changed = True
            if last_name and getattr(user, 'last_name', None) != last_name:
                user.last_name = last_name
                changed = True
            if changed:
                user.save()
        except Exception:
            pass

        request.session.pop('codigo_verificacion', None)
        request.session.pop('correo_verificacion', None)
        request.session.pop('codigo_expira', None)

        return redirect('login')

    return render(request, 'registro.html')
