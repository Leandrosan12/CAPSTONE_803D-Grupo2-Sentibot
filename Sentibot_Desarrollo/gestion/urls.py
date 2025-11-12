from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('camara/', views.camara, name='camara'),
    path('agenda/', views.agenda, name='agenda'),
    path('emociones-data/', views.emociones_data, name='emociones_data'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path('actividades/', views.actividades, name='actividades'), 
    path('opciones/', views.opciones, name='opciones'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
    path('extra/', views.extra, name='extra'),
    path('modulo_profesor/', views.modulo_profesor, name='modulo_profesor'),
    path('modulo/', views.modulo, name='modulo'),
    path('modulo/escuelas/', views.escuelas, name='escuelas'),
    path('modulo/alumnos/', views.alumnos, name='alumnos'),
    path('modulo/detalle_alumno/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),
    path("predict_emotion/", views.predict_emotion_view, name="predict_emotion"),
    path("procesar_emocion_camara/<int:sesion_id>/", views.procesar_emocion_camara, name="procesar_emocion_camara"),
    path("seleccionar_emocion/<str:emocion_nombre>/", views.seleccionar_emocion, name="seleccionar_emocion"),
    path("actividades/<str:emocion_nombre>/", views.mostrar_actividades, name="mostrar_actividades"),
    path('dashboard_emociones/', views.dashboard_emociones, name='dashboard_emociones'),
    path('encuesta_satisfaccion/', views.encuesta_satisfaccion, name='encuesta_satisfaccion'),
]
