from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Count
from django.db import connection
from weasyprint import HTML

from gestion.models import Usuario, Emocion, EmocionReal, Sesion

User = get_user_model()


# ------------------------------
# Vistas de autenticación
# ------------------------------

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html', {'user': request.user})


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
# Vistas principales
# ------------------------------

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
    html = template.render({"nombre": "Usuario de Prueba"})
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    return response


def reporte(request):
    return render(request, 'reporte.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def actividades(request):
    return render(request, 'actividades.html')


# ------------------------------
# Vistas con datos
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
        "values": [row[1] for row in rows]
    }
    return JsonResponse(data)


# gestion/views.py
from django.shortcuts import render
from .models import EmocionReal
from django.db.models import Count

def seguimiento(request):
    datos = EmocionReal.objects.values('emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion'] for d in datos]
    valores = [d['total'] for d in datos]

    return render(request, 'seguimiento.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })

from django.shortcuts import render
from .models import EmocionCamara

from django.db import connection
from django.shortcuts import render

def lista_usuarios(request):
    # Ejecutamos la vista directamente
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_emociones_camara")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    context = {
        'emociones': datos
    }
    return render(request, 'lista_usuarios.html', context)



def dashboard_emociones(request):
    # Ejecutamos la vista directamente
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_emociones_camara")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    context = {
        'emociones': datos
    }
    return render(request, 'dashboard_emociones.html', context)