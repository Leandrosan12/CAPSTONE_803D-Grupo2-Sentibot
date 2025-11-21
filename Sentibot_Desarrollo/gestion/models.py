from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# ------------------------------
# ROLES Y ESCUELAS
# ------------------------------

class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Escuela(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# ------------------------------
# USUARIO PERSONALIZADO
# ------------------------------

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name="usuarios")
    escuela = models.ForeignKey(Escuela, on_delete=models.SET_NULL, null=True, related_name="usuarios")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Se elimina username como obligatorio

    def __str__(self):
        return self.email


# ------------------------------
# SESIONES Y EMOCIONES
# ------------------------------

class Sesion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sesiones")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def cerrar(self):
        if self.activa:
            self.fecha_fin = timezone.now()
            self.activa = False
            self.save()

    def __str__(self):
        estado = "Activa" if self.activa else "Cerrada"
        return f"Sesión {self.id} - {self.usuario.email} ({estado})"


class Emocion(models.Model):
    nombre_emocion = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_emocion


class EmocionCamara(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="emociones_camara")
    nombre_emocion = models.CharField(max_length=50)
    probabilidad = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_emocion} - {self.sesion.usuario.email}"


class EmocionReal(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="emociones_reales")
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE, related_name="emociones_reales")
    tipo_emocion = models.CharField(max_length=50)
    porcentaje = models.FloatField(default=0.0)

    def calcular_porcentaje(self):
        registros = self.sesion.emociones_camara.filter(nombre_emocion__iexact=self.tipo_emocion)
        if registros.exists():
            promedio = sum(r.probabilidad for r in registros) / registros.count()
            self.porcentaje = round(promedio, 2)
        else:
            self.porcentaje = 0.0
        self.save()

    def __str__(self):
        return f"{self.tipo_emocion} - {self.sesion.usuario.email} ({self.porcentaje}%)"


# ------------------------------
# ACTIVIDADES
# ------------------------------

class Actividad(models.Model):
    nombre_actividad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    importancia = models.TextField(blank=True, null=True)
    como_realizarla = models.TextField(blank=True, null=True)
    recurso = models.TextField(blank=True, null=True)
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE, related_name="actividades")

    def __str__(self):
        return self.nombre_actividad


# ------------------------------
# ENCUESTAS
# ------------------------------

class Encuesta(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Pregunta(models.Model):
    texto = models.TextField()
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="preguntas")

    def __str__(self):
        return self.texto[:50]



# ------------------------------
# REPORTES
# ------------------------------

class Reporte(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reportes")
    tipo_reporte = models.CharField(max_length=50)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.usuario.email}"


# ------------------------------
# EMOTION SESSION (RESUMEN)
# ------------------------------

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
        return f"Sesión de {self.user} - {self.fecha}"


# ------------------------------
# VISTA EXTERNA: STUDENT
# ------------------------------






# ------------------------------
# ENCUESTA SATISFACCIÓN
# ------------------------------

class EncuestaSatisfaccion(models.Model):
    sesion = models.OneToOneField(
        'Sesion',
        on_delete=models.CASCADE,
        related_name='encuesta',
        null=True,
        blank=True
    )
    utilidad = models.CharField(max_length=50)
    recomendacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encuesta sesión {self.sesion.id if self.sesion else 'sin sesión'} - {self.utilidad}"
