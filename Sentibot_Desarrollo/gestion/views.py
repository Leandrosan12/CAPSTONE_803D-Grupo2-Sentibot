from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse
import json, base64, requests
from random import randint, sample

from .models import Usuario, Sesion, Emocion, EmocionCamara, EmocionReal, Actividad, EncuestaSatisfaccion

User = get_user_model()
FASTAPI_URL = "https://negational-kerry-untoward.ngrok-free.dev/predict_emotion/"


# ============================================================
# LOGIN / LOGOUT
# ============================================================
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


# ============================================================
# REGISTRO
# ============================================================
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


# ============================================================
# VISTAS PRINCIPALES
# ============================================================
@login_required(login_url='login')
def home(request):
    return render(request, "home.html", {"user": request.user})


@login_required(login_url='login')
def perfil(request):
    return render(request, 'perfil.html')


@login_required(login_url='login')
def camara(request):
    # Cerrar sesiones previas abiertas
    Sesion.objects.filter(usuario=request.user, activa=True).update(activa=False, fecha_fin=timezone.now())

    # Crear una nueva sesión activa
    sesion = Sesion.objects.create(usuario=request.user, activa=True)

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
@login_required
def actividades(request):
    return render(request, 'actividades.html')


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

from django.views.decorators.http import require_POST
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

@login_required
def procesar_encuesta(request):
    if request.method == "POST":
        # Aquí procesas las respuestas de la encuesta
        respuestas = request.POST

        # Cerrar la sesión activa si existe
        sesion = Sesion.objects.filter(usuario=request.user, activa=True).first()
        if sesion:
            sesion.cerrar()

        messages.success(request, "Gracias por completar la encuesta.")
        return redirect("inicio")  # o a tus recomendaciones

from django.shortcuts import redirect
from .models import Sesion

def finalizar_y_encuesta(request):
    sesion = Sesion.objects.filter(usuario=request.user, activa=True).order_by('-fecha_inicio').first()
    if sesion:
        sesion.cerrar()  # ✅ aquí se registra fecha_fin correctamente
    return redirect('encuesta_satisfaccion')
