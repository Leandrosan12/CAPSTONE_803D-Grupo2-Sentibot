# views.py limpio y funcional

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import connection
from .models import Sesion, EmocionCamara, Usuario
from gestion.models import Usuario as GestionUsuario, Emocion, EmocionReal, Sesion as GestionSesion

User = get_user_model()

# ------------------------------
# LOGIN / LOGOUT
# ------------------------------
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
# REGISTRO NORMAL
# ------------------------------
def registro(request):
    if request.method == "POST":
        email = request.POST.get('correo')
        password = request.POST.get('contrasena')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'registro.html', {'error': 'Correo ya registrado'})

        # Generar username automático a partir del email
        username = email.split('@')[0]

        user = User.objects.create_user(
            username=username,   # ⚡ obligatorio para AbstractUser
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        auth_login(request, user)
        return redirect('camara')

    return render(request, 'registro.html')



# ------------------------------
# VISTAS PRINCIPALES
# ------------------------------
@login_required(login_url='login')
def home(request):
    return render(request, "home.html", {"user": request.user})


@login_required(login_url='login')
def perfil(request):
    return render(request, 'perfil.html')


@login_required(login_url='login')
def camara(request):
    sesion = Sesion.objects.filter(usuario=request.user, fecha_fin__isnull=True).first()
    if not sesion:
        sesion = Sesion.objects.create(usuario=request.user)
    return render(request, "camara.html", {"sesion_id": sesion.id})


def extra(request):
    return render(request, 'extra.html')


def agenda_view(request):
    return render(request, 'agenda.html')


# ------------------------------
# MÓDULOS PRINCIPALES
# ------------------------------
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


def detalle_alumno(request, id):
    alumno = get_object_or_404(Usuario, id=id)
    return render(request, 'modulo/detalle_alumno.html', {'alumno': alumno})


def escuelas(request):
    escuelas = [
        {'id': 1, 'nombre': 'Escuela de Ingeniería', 'carreras': ['Informática', 'Civil', 'Industrial'], 'sede': 'Santiago'},
        {'id': 2, 'nombre': 'Escuela de Construcción', 'carreras': ['Construcción', 'Arquitectura'], 'sede': 'Quilpué'},
        {'id': 3, 'nombre': 'Escuela de Medicina', 'carreras': ['Medicina', 'Enfermería'], 'sede': 'Concepción'},
    ]
    return render(request, 'escuelas.html', {'escuelas': escuelas})


# ------------------------------
# ACTIVIDADES
# ------------------------------
def actividades(request):
    return render(request, 'actividades.html')


def mantenimiento(request):
    return render(request, 'mantenimiento.html')


# ------------------------------
# SEGUIMIENTO / EMOCIONES
# ------------------------------
def seguimiento(request):
    emociones = EmocionCamara.objects.values('nombre_emocion').annotate(cantidad=Count('id'))
    emociones = list(emociones)

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


def predict_emotion_view(request):
    # Mantengo la función tal como estaba
    pass


def dashboard_emociones(request):
    datos = EmocionReal.objects.values('emocion__nombre_emocion').annotate(total=Count('emocion'))
    etiquetas = [d['emocion__nombre_emocion'] for d in datos]
    valores = [d['total'] for d in datos]
    return render(request, 'dashboard_emociones.html', {
        'emociones_labels': etiquetas,
        'emociones_counts': valores,
    })


def lista_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gestion_usuario")
        columnas = [col[0] for col in cursor.description]
        datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    return render(request, 'lista_usuarios.html', {'usuarios': datos})
