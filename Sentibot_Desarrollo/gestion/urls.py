from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', views.login, name='login'),    
    path('home/', home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('camara/', views.camara, name='camara'),
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path("emociones-data/", views.emociones_data, name="emociones_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('actividades/', views.actividades, name='actividades'), 
    path('seguimiento/', views.seguimiento, name='seguimiento'),
    path('dashboard_emociones/', views.dashboard_emociones, name='dashboard_emociones'),
    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
]
