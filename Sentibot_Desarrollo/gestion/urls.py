from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('camara/', views.camara, name='camara'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path("emociones-data/", views.emociones_data, name="emociones_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('emociones_data/', views.emociones_data, name='emociones_data'),
    path('predict_emotion/', views.predict_emotion_view, name='predict_emotion')
    path('actividades/', views.actividades, name='actividades'), 

    path('dashboard_emociones/', views.dashboard_emociones, name='dashboard_emociones'),
    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('extra/', views.extra, name='extra'),
    path('modulo/', views.modulo, name='modulo')
    
]

