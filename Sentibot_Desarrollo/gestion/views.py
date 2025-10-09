from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from gestion.models import Usuario  
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()


def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'El email ya está registrado'})

        User.objects.create_user(
            username=email, 
            email=email,
            password=password
        )
        return redirect('login') 

    return render(request, 'registro.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get('correo')      # coincide con tu formulario
        password = request.POST.get('contrasena')

        # Autenticar usando email como USERNAME_FIELD
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('camara')  # redirección exitosa
        else:
            return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'login.html')




# Logout
def logout_view(request):
    auth_logout(request)
    return redirect('login')

# Home
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html', {'user': request.user})

    
def perfil(request):
    return render(request, 'perfil.html')
def camara(request):
    return render(request, 'camara.html')



def seguimiento(request):
    return render(request, 'seguimiento.html')
def dashboard(request):
    return render(request, 'dashboard.html')




from django.http import JsonResponse
from django.db import connection

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
        "values": [row[1] for row in rows]
    }
    return JsonResponse(data)

