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
