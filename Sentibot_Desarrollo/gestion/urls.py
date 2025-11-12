from django.urls import path
from . import views

urlpatterns = [
    # --- Autenticación ---
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),

    # --- Páginas principales ---
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('camara/', views.camara, name='camara'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('extra/', views.extra, name='extra'),

    # --- Módulos principales ---
    path('modulo/', views.modulo, name='modulo'),
    path('modulo_profesor/', views.modulo_profesor, name='modulo_profesor'),

    # --- Escuelas y Alumnos ---
    path('modulo/escuelas/', views.escuelas, name='escuelas'),
    path('modulo/alumnos/', views.alumnos, name='alumnos'),
    path('modulo/detalle_alumno/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),

    # --- Emociones y Dashboards ---
    path('emociones-data/', views.emociones_data, name='emociones_data'),
    path('predict_emotion/', views.predict_emotion_view, name='predict_emotion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard_emociones/', views.dashboard_emociones, name='dashboard_emociones'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),

    # --- Otros módulos ---
    path('actividades/', views.actividades, name='actividades'),
    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
]
