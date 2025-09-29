from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', views.login, name='login'),    
    path('home', home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('camara/', views.camara, name='camara'),
    path('reporte/', views.reporte, name='reporte'),
    path('formulario/', views.formulario, name='formulario'),
]
