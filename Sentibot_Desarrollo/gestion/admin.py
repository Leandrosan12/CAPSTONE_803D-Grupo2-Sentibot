from django.contrib import admin
from .models import (
    Sala, Emocion, Pregunta, Actividad, Sesion, Respuesta, 
    EncuestaSatisfaccion, Reporte
)

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion')

@admin.register(Emocion)
class EmocionAdmin(admin.ModelAdmin):
    list_display = ('nombre_emocion',)

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('texto_pregunta', 'emocion')

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre_actividad', 'emocion')

@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'sala', 'fecha_hora_inicio', 'emocion_inicial', 'emocion_confirmada')

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'pregunta', 'respuesta')

@admin.register(EncuestaSatisfaccion)
class EncuestaSatisfaccionAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'puntaje', 'fecha')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'fecha_generacion')


