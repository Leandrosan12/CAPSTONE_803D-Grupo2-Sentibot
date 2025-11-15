from django.urls import path
from . import views

urlpatterns = [
    # --- 🔐 Autenticación ---
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),

    # --- 🏠 Páginas principales ---
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('camara/', views.camara, name='camara'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path('actividades/', views.actividades, name='actividades'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
    path('extra/', views.extra, name='extra'),

    # --- 🧩 Módulos principales ---
    path('modulo/', views.modulo, name='modulo'),

    # --- 👨‍🏫 Módulo del profesor ---
    path('modulo_profesor/', views.modulo_profesor, name='modulo_profesor'),  # Vista principal del módulo profesor
    path('grafico_profesor/', views.grafico_profesor, name='grafico_profesor'),  # Dashboard emocional del profesor

    # --- 🏫 Escuelas y Alumnos ---
    path('modulo/escuelas/', views.escuelas, name='escuelas'),
    path('modulo/alumnos/', views.alumnos, name='alumnos'),
    path('modulo/detalle_alumno/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),

    # --- 📧 Verificación de correo ---
    path('enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),

    # --- 🤖 API de emociones ---
    path('api/registrar_emocion/', views.registrar_emocion, name='registrar_emocion'),
    path('api/predict_emotion/', views.predict_emotion_view, name='predict_emotion'),
    path('api/emociones_data/', views.emociones_data, name='emociones_data'),
]
