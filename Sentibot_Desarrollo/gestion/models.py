from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  # 👈 Esto trae el modelo de usuario correcto según AUTH_USER_MODEL


    

# ------------------------------
# Rol
# ------------------------------
class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ------------------------------
# Escuela
# ------------------------------
class Escuela(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ------------------------------
# Usuario (extendemos AbstractUser)
# ------------------------------
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)  # <- ahora es único
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="usuarios", null=True)
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE, related_name="usuarios", null=True)

    REQUIRED_FIELDS = []  
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


# ------------------------------
# Reportes
# ------------------------------
class Reporte(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reportes")
    tipo_reporte = models.CharField(max_length=50)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.usuario.username}"

# ------------------------------
# Emociones
# ------------------------------
class Emocion(models.Model):
    nombre_emocion = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_emocion

# ------------------------------
# Sesión
# ------------------------------
class Sesion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sesiones")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Sesion {self.id} - {self.usuario.username}"

# ------------------------------
# Encuesta
# ------------------------------
class Encuesta(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ------------------------------
# Preguntas
# ------------------------------
class Pregunta(models.Model):
    texto = models.TextField()
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="preguntas")

    def __str__(self):
        return self.texto[:50]

# ------------------------------
# Respuesta Encuesta
# ------------------------------
class RespuestaEncuesta(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="respuestas")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="respuestas_encuesta")
    respuesta = models.TextField()

    def __str__(self):
        return f"Respuesta Encuesta {self.encuesta.nombre} - {self.usuario.username}"

# ------------------------------
# Respuesta Pregunta
# ------------------------------
class RespuestaPregunta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="respuestas")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="respuestas_preguntas")
    respuesta = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.pregunta.texto[:30]}"

# ------------------------------
# Emoción Cámara
# ------------------------------
class EmocionCamara(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="emociones_camara")
    nombre_emocion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    probabilidad = models.FloatField()

    def __str__(self):
        return f"{self.nombre_emocion} - {self.sesion.usuario.username}"

# ------------------------------
# Emoción Real
# ------------------------------
class EmocionReal(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="emociones_reales")
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE, related_name="emociones_reales")
    tipo_emocion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tipo_emocion} - {self.sesion.usuario.username}"

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
# Modulos
# ------------------------------

from django.db import models

class School(models.Model):
    name = models.CharField(max_length=200)
    sede = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    sede = models.CharField(max_length=100)
    edad = models.PositiveIntegerField(null=True, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    school = models.ForeignKey(School, related_name='students', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"
    class Meta:
        managed = False  # Django no crea ni modifica esta tabla
        db_table = 'vw_emociones_camara'
    

from django.db import models
from django.contrib.auth.models import User

class EmotionSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    feliz_seg = models.IntegerField(default=0)
    feliz_pct = models.FloatField(default=0.0)

    triste_seg = models.IntegerField(default=0)
    triste_pct = models.FloatField(default=0.0)

    neutral_seg = models.IntegerField(default=0)
    neutral_pct = models.FloatField(default=0.0)

    enojado_seg = models.IntegerField(default=0)
    enojado_pct = models.FloatField(default=0.0)

    sorprendido_seg = models.IntegerField(default=0)
    sorprendido_pct = models.FloatField(default=0.0)

    sinreconocer_seg = models.IntegerField(default=0)
    sinreconocer_pct = models.FloatField(default=0.0)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sesión de {self.user or 'Anónimo'} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
