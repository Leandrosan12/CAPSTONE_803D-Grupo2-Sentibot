from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages




def home(request):
    return render(request, 'index.html')    

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


USUARIO_PRUEBA = {
    "correo": "test@correo.com",
    "contrasena": "1234"
}

def login(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        
        # Opción 1: usuario fijo
        if correo == USUARIO_PRUEBA["correo"] and contrasena == USUARIO_PRUEBA["contrasena"]:
            return redirect("home")

        # Opción 2: usuario registrado en la base de datos
        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Correo o contraseña incorrectos")
            return redirect("login")

    return render(request, "login.html")

def perfil(request):
    return render(request, 'perfil.html')

# 👇 Nueva vista
def actividades(request):
    return render(request, 'actividades.html')
    
def seguimiento(request):
    return render(request, 'seguimiento.html')