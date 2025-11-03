from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('camara/', views.camara, name='camara'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path('actividades/', views.actividades, name='actividades'), 
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),  # actualizado

    path('extra/', views.extra, name='extra'),
    path('modulo_profesor/', views.modulo_profesor, name='modulo_profesor'),
    path('modulo/', views.modulo, name='modulo'),
    path('modulo/escuelas/', views.escuelas, name='escuelas'),
    path('modulo/alumnos/', views.alumnos, name='alumnos'),
    path('modulo/detalle_alumno/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),

    # ✅ Ruta para la API externa de predicción de emociones

    

    path('detalle/<int:id>/', views.detalle_alumno, name='detalle_alumno'),

# verificar correo 

    path('enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),


    
]
