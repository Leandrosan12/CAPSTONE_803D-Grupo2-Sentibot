from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('actividades/', views.actividades, name='actividades'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path('logout/', views.logout_view, name='logout'),
    path('camara/', views.camara, name='camara'),
    
    path('emociones-data/', views.emociones_data, name='emociones_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('extra/', views.extra, name='extra'),
]
