from django.db import models
from django.contrib.auth.models import User

<<<<<<< HEAD
=======
# ------------------------------
# Sala
# ------------------------------
class Sala(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ------------------------------
# Emocion
# ------------------------------
class Emocion(models.Model):
    nombre_emocion = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_emocion

# ------------------------------
# Pregunta
# ------------------------------
class Pregunta(models.Model):
    texto_pregunta = models.TextField()
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE, related_name="preguntas")

    def __str__(self):
        return self.texto_pregunta[:50]

# ------------------------------
# Actividad
# ------------------------------
class Actividad(models.Model):
    nombre_actividad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE, related_name="actividades")

    def __str__(self):
        return self.nombre_actividad

# ------------------------------
# Sesion
# ------------------------------
class Sesion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sesiones")
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="sesiones")
    fecha_hora_inicio = models.DateTimeField(auto_now_add=True)
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)
    emocion_inicial = models.ForeignKey(Emocion, on_delete=models.SET_NULL, null=True, blank=True, related_name="sesiones_iniciales")
    emocion_confirmada = models.ForeignKey(Emocion, on_delete=models.SET_NULL, null=True, blank=True, related_name="sesiones_confirmadas")
    
    preguntas = models.ManyToManyField(Pregunta, through='Respuesta', related_name='sesiones')

    def __str__(self):
        return f"Sesion {self.id} - {self.usuario.username}"

# ------------------------------
# Respuesta
# ------------------------------
class Respuesta(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="respuestas")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="respuestas")
    respuesta = models.TextField()

    def __str__(self):
        return f"{self.sesion} - Pregunta {self.pregunta.id}"

# ------------------------------
# Encuesta de Satisfaccion
# ------------------------------
class EncuestaSatisfaccion(models.Model):
    sesion = models.OneToOneField(Sesion, on_delete=models.CASCADE, related_name="encuesta")
    puntaje = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encuesta Sesion {self.sesion.id}"

# ------------------------------
# Reporte
# ------------------------------
TIPO_REPORTE = [
    ('individual', 'Individual'),
    ('global', 'Global')
]

class Reporte(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reportes")  # psicóloga o admin
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_REPORTE)

    def __str__(self):
        return f"Reporte {self.tipo} - {self.usuario.username} - {self.fecha_generacion.date()}"


<<<<<<< HEAD
=======
    def __str__(self):
        return self.nombre_area
    

    

>>>>>>> 7b018d93d72a4dd9ab805114f84ccbe1746fc1ec
>>>>>>> 653918ca86d64d9cfac87c1efe0684436af9160b
