from django.shortcuts import render

def home(request):
    return render(request, 'index.html')
def perfil(request):
    return render(request, 'perfil.html') 