from django.urls import path
from . import views
from .views import emociones_por_escuela, tiempo_promedio_sesion_por_escuela

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
    path('registrar_emocion_manual/', views.registrar_emocion_manual, name='registrar_emocion_manual'),
    # Actividades usando query param (ya no necesitas path param)
    path('actividades/', views.actividades, name='actividades'),  # primero la ruta sin parámetro
    path('actividades/<str:emocion_nombre>/', views.mostrar_actividades, name='mostrar_actividades'),  # luego la con parámetro


    path('opciones/', views.opciones, name='opciones'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
    path('extra/', views.extra, name='extra'),

    # --- 🧩 Módulos principales ---
    path('modulo/', views.modulo, name='modulo'),

    # --- 👨‍🏫 Módulo del profesor ---
    path('modulo_profesor/', views.modulo_profesor, name='modulo_profesor'),  # Vista principal del módulo profesor
    path('grafico_profesor/', views.grafico_profesor, name='grafico_profesor'),  # Dashboard emocional del profesor

    # --- 🏫 Escuelas y Alumnos ---
    path('modulo/alumnos/', views.alumnos, name='alumnos'),
    path('modulo/detalle_alumno/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),

    # --- 📧 Verificación de correo ---
    path('enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),

    # --- 🤖 API de emociones ---
    path('api/registrar_emocion/', views.registrar_emocion, name='registrar_emocion'),
    path('api/predict_emotion/', views.predict_emotion_view, name='predict_emotion'),
    path('api/emociones_data/', views.emociones_data, name='emociones_data'),
    path("predict_emotion/", views.predict_emotion_view, name="predict_emotion"),
    path("procesar_emocion_camara/<int:sesion_id>/", views.procesar_emocion_camara, name="procesar_emocion_camara"),
    path("seleccionar_emocion/<str:emocion_nombre>/", views.seleccionar_emocion, name="seleccionar_emocion"),


    path('dashboard_emociones/', views.dashboard_emociones, name='dashboard_emociones'),
    path('encuesta_satisfaccion/', views.encuesta_satisfaccion, name='encuesta_satisfaccion'),
    path('preguntas/', views.preguntas, name='preguntas'),
    path('cerrar_sesion_ajax/', views.cerrar_sesion_ajax, name='cerrar_sesion_ajax'),

    path('finalizar_y_encuesta/', views.finalizar_y_encuesta, name='finalizar_y_encuesta'),
    path('resultado/', views.mostrar_resultado, name='mostrar_resultado'),

    #panel admin
    # PANEL ADMIN PERSONALIZADO

    path('actividadesconf/', views.admin_actividades, name='actividadesconf'),
    path('actividadesconf/editar/<int:id>/', views.editar_actividad, name='editar_actividad'),
    path('actividadesconf/eliminar/<int:id>/', views.eliminar_actividad, name='eliminar_actividad'),
    path('actividadesconf/crear/', views.crear_actividad, name='crear_actividad'),
    path("emociones/por-escuela/", emociones_por_escuela, name="emociones_por_escuela"),
    path('dashboard-emocional/<int:escuela_id>/',views.grafico_profesor, name='dashboard_emocional'),
    path('dashboard/tiempo-promedio-sesion/<int:escuela_id>/', tiempo_promedio_sesion_por_escuela, name="tiempo_promedio_sesion_por_escuela"),
    path('actualizar_alumno/<int:alumno_id>/', views.actualizar_alumno, name='actualizar_alumno'),
    path('eliminar_alumno/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),

    
    path("recuperar-contrasena/", views.recuperar_contrasena, name="recuperar_contrasena"),
    path("confirmar-contrasena/", views.confirmar_contrasena, name="confirmar_contrasena"),



]
