from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return self.nombre_area
    

    
    


    #prueba vista dashboard

class EmocionCamara(models.Model):
    id_usuario = models.IntegerField()
    nombre_completo = models.CharField(max_length=255)
    rol = models.CharField(max_length=100)
    escuela = models.CharField(max_length=100)
    id_sesion = models.IntegerField()
    id_emocion = models.IntegerField()
    emocion_camara = models.CharField(max_length=100)
    emocion_real = models.CharField(max_length=100)
    probabilidad = models.FloatField()
    fecha_emocion_inicio = models.DateTimeField()
    fecha_emocion_fin = models.DateTimeField()

    class Meta:
        managed = False  # Django no crea ni modifica esta tabla
        db_table = 'vw_emociones_camara'
