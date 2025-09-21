from django.shortcuts import render

def home(request):
    return render(request, 'index.html')
def registro(request):
    return render(request, 'registro.html')
def login(request):
    return render(request, 'login.html')



    
def perfil(request):
    return render(request, 'perfil.html')
