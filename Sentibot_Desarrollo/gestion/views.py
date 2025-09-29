from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
import hashlib





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
        
               # Opción 1: usuario fijo ESTO ES SOLO TEMPORAL BASTA QUE SE CREE LA BD
        if correo == USUARIO_PRUEBA["correo"] and contrasena == USUARIO_PRUEBA["contrasena"]:
            return redirect("camara")
        # Opción 2: usuario registrado en la base de datos
        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect("camara")
        else:
            messages.error(request, "Correo o contraseña incorrectos")
            return redirect("login")

    return render(request, "login.html")



    
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
