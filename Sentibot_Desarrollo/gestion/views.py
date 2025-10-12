from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from django.db import connection


# Usuario de prueba
USUARIO_PRUEBA = {
    "correo": "test@correo.com",
    "contrasena": "1234"
}

# ------------------------------
# LOGIN
# ------------------------------
def login(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")

        # Usuario de prueba
        if correo == USUARIO_PRUEBA["correo"] and contrasena == USUARIO_PRUEBA["contrasena"]:
            return redirect("home")

        # Usuario real de la base de datos
        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            auth_login(request, user)
            return redirect("camara")
        else:
            messages.error(request, "Correo o contraseña incorrectos")
            return render(request, "login.html")

    return render(request, "login.html")


# ------------------------------
# REGISTRO
# ------------------------------
def registro(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")

        if User.objects.filter(username=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("registro")

        user = User.objects.create_user(username=correo, email=correo, password=contrasena)
        user.save()
        messages.success(request, "Cuenta creada con éxito. Ahora inicia sesión.")
        return redirect("login")

    return render(request, "registro.html")


# ------------------------------
# HOME
# ------------------------------
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home.html", {"user": request.user})


# ------------------------------
# PERFIL
# ------------------------------
def perfil(request):
    return render(request, "perfil.html")


# ------------------------------
# ACTIVIDADES
# ------------------------------
def actividades(request):
    return render(request, "actividades.html")


# ------------------------------
# SEGUIMIENTO
# ------------------------------
def seguimiento(request):
    return render(request, "seguimiento.html")


# ------------------------------
# CÁMARA
# ------------------------------
def camara(request):
    return render(request, "camara.html")
def extra(request):
    return render(request, 'extra.html')






def dashboard(request):
    return render(request, "dashboard.html")


# ------------------------------
# LOGOUT
# ------------------------------
def logout_view(request):
    auth_logout(request)
    return redirect("login")


# ------------------------------
# EMOCIONES DATA (JSON para gráficos)
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
