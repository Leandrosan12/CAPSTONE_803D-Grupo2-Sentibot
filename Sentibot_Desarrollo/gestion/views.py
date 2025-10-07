from django.shortcuts import render, redirect
<<<<<<< HEAD
=======
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
>>>>>>> ef09a7ebc1310a687b0d9de8ddcdcf0aeeab57d2
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from gestion.models import Usuario  
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()


<<<<<<< HEAD
=======


def home(request):
    return render(request, 'index.html')    

>>>>>>> ef09a7ebc1310a687b0d9de8ddcdcf0aeeab57d2
def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

<<<<<<< HEAD
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
=======
        if User.objects.filter(username=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("registro")
        
        user = User.objects.create_user(username=correo, email=correo, password=contrasena)
        user.save()
        messages.success(request, "Cuenta creada con éxito. Ahora inicia sesión.")
        return redirect("login")
>>>>>>> ef09a7ebc1310a687b0d9de8ddcdcf0aeeab57d2

    return render(request, 'registro.html')


def login(request):
    if request.method == "POST":
<<<<<<< HEAD
        email = request.POST.get('correo')      # coincide con tu formulario
        password = request.POST.get('contrasena')

        # Autenticar usando email como USERNAME_FIELD
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('camara')  # redirección 
=======
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
>>>>>>> ef09a7ebc1310a687b0d9de8ddcdcf0aeeab57d2
        else:
            return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'login.html')

<<<<<<< HEAD



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
def formulario(request):
    if request.method == "POST":
        data = {
            "nombre": request.POST.get("nombre"),
            "motivo": request.POST.get("motivo"),
            "historia": request.POST.get("historia"),
            "evaluacion": request.POST.get("evaluacion"),
            "analisis": request.POST.get("analisis"),
            "conclusiones": request.POST.get("conclusiones"),
            "recomendaciones": request.POST.get("recomendaciones"),
            "actividades": request.POST.getlist("actividades"),
        }
        template = get_template("reporte.html")
        html = template.render(data)
        pdf = HTML(string=html).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        return response

    return render(request, "formulario.html")
def generar_pdf(request):
    template = get_template("reporte.html")
    html = template.render({
        "nombre": "Usuario de Prueba"
    })
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    return response
def reporte(request):
    return render(request, 'reporte.html')
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

=======
def perfil(request):
    return render(request, 'perfil.html')

# 👇 Nueva vista
def actividades(request):
    return render(request, 'actividades.html')
    
def seguimiento(request):
    return render(request, 'seguimiento.html')
>>>>>>> ef09a7ebc1310a687b0d9de8ddcdcf0aeeab57d2
