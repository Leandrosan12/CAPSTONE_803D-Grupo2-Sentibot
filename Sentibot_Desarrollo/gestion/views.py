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
# Páginas principales
# ------------------------------
def perfil(request):
    return render(request, 'perfil.html')



@login_required(login_url='login')  # ajusta la URL si la llamas distinto
def camara(request):
    # Obtener o crear sesión activa solo para usuarios autenticados
    sesion = Sesion.objects.filter(usuario=request.user, fecha_fin__isnull=True).first()
    if not sesion:
        sesion = Sesion.objects.create(usuario=request.user, inicio=timezone.now())
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


def lista_usuarios(request):
    return render(request, 'lista_usuarios.html')

def dashboard_emociones(request):
    sesion, created = Sesion.objects.get_or_create(usuario=request.user, fecha_fin__isnull=True)
    return render(request, "dashboard_emociones.html", {"sesion": sesion})


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
