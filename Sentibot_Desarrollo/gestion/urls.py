from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', views.login, name='login'),    
    path('home', home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('reporte/', views.reporte, name='reporte'),
    path('formulario/', views.formulario, name='formulario'),
    path('pruebas/', views.pruebas, name='pruebas'),
    path('escuelas/', views.escuelas, name='escuelas'),
    path('actividades/', views.actividades, name='actividades'),
    path('camara/', views.camara, name='camara'),

    
]
