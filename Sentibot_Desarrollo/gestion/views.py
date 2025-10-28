from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Count
from django.db import connection
from gestion.models import Usuario, Emocion, EmocionReal, Sesion
User = get_user_model()
# ------------------------------
# Autenticación
# ------------------------------
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

def camara(request):
    # Obtener o crear sesión activa
    sesion, created = Sesion.objects.get_or_create(usuario=request.user, fecha_fin__isnull=True)
    return render(request, "camara.html", {"sesion_id": sesion.id})

def extra(request):
    return render(request, 'extra.html')

def agenda_view(request):
    return render(request, 'agenda.html')

def modulo(request):
    return render(request, 'modulo/modulo.html')

def modulo_profesor(request):
    return render(request, 'modulo_profesor.html')

def alumnos(request):
    return render(request, 'modulo/alumnos.html')

def detalle_alumno(request, alumno_id):
    return render(request, 'modulo/detalle_alumno.html', {'alumno_id': alumno_id})

def escuelas(request):
    return render(request, 'modulo/escuelas.html')

def actividades(request):
    return render(request, 'actividades.html')

def mantenimiento(request):
    return render(request, 'mantenimiento.html')

def seguimiento(request):
    return render(request, 'seguimiento.html')

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
