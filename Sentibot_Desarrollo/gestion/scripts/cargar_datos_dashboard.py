import os
import django
import random
from datetime import timedelta
from django.utils import timezone  # Para fechas aware

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from gestion.models import Usuario, Escuela, Sesion, Emocion, EmocionReal, Encuesta, RespuestaEncuesta


def run():
    print("🌱 Insertando datos REALES para el dashboard...")

    # ============================
    # 1. CREAR ESCUELAS
    # ============================
    escuelas = []
    nombres_escuelas = [
        "Escuela de Informática y Telecomunicaciones",
        "Escuela de Administración y Negocios",
        "Escuela de Ingeniería y Recursos Naturales",
        "Escuela de Salud y Bienestar",
        "Escuela de Construcción"
    ]

    for nombre in nombres_escuelas:
        escuela, _ = Escuela.objects.get_or_create(
            nombre=nombre,
            defaults={"sede": "Melipilla"}
        )
        escuelas.append(escuela)

    print(f"✔ {len(escuelas)} escuelas creadas/listas")

    # ============================
    # 2. CREAR USUARIOS
    # ============================
    usuarios = []
    for i in range(10):
        escuela = random.choice(escuelas)
        user, _ = Usuario.objects.get_or_create(
            email=f"user{i}@mail.com",
            defaults={
                "username": f"user{i}@mail.com",
                "escuela": escuela
            }
        )
        usuarios.append(user)

    print("✔ 10 usuarios creados/listos")

    # ============================
    # 3. CREAR INSTANCIAS DE EMOCION
    # ============================
    tipos_emocion = ["Alegría", "Tristeza", "Neutral", "Enojo", "Sorpresa", "Miedo"]
    emociones_obj = {}
    for nombre in tipos_emocion:
        emocion, _ = Emocion.objects.get_or_create(nombre_emocion=nombre)
        emociones_obj[nombre] = emocion

    # ============================
    # 4. CREAR SESIONES + EMOCIONES REALES
    # ============================
    num_sesiones = 80

    for _ in range(num_sesiones):
        user = random.choice(usuarios)

        # Fechas aware
        dias_atras = random.randint(1, 30)
        fecha_inicio = timezone.now() - timedelta(days=dias_atras, minutes=random.randint(10, 60))
        duracion_minutos = random.randint(1, 5)
        fecha_fin = fecha_inicio + timedelta(minutes=duracion_minutos)

        # Crear sesión
        sesion = Sesion.objects.create(
            usuario=user,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        # Crear emociones reales
        num_emociones_registradas = random.randint(3, 6)
        porcentajes_crudos = [random.uniform(5, 40) for _ in range(num_emociones_registradas)]
        total_crudo = sum(porcentajes_crudos)
        porcentajes_normalizados = [(p / total_crudo) * 100 for p in porcentajes_crudos]

        emociones_a_registrar = random.sample(tipos_emocion, num_emociones_registradas)

        for tipo, porcentaje in zip(emociones_a_registrar, porcentajes_normalizados):
            EmocionReal.objects.create(
                sesion=sesion,
                tipo_emocion=tipo,
                emocion=emociones_obj[tipo],  # ⚡ Instancia correcta de Emocion
                # ⚡ Si quieres guardar el porcentaje/intensidad:
                # valor=round(porcentaje, 2)
            )

    print(f"✔ {num_sesiones} sesiones y emociones reales insertadas")

    # ============================
    # 5. CREAR ENCUESTAS + RESPUESTAS
    # ============================
    encuestas = []
    nombres_encuestas = ["Encuesta satisfacción", "Encuesta clase", "Encuesta emoción"]

    for n in nombres_encuestas:
        e, _ = Encuesta.objects.get_or_create(
            nombre=n,
            defaults={
                "tipo": "si/no",
                "descripcion": "Encuesta generada automáticamente"
            }
        )
        encuestas.append(e)

    for user in usuarios:
        for encuesta in encuestas:
            respuesta_texto = random.choice(["si", "no"])
            RespuestaEncuesta.objects.get_or_create(
                usuario=user,
                encuesta=encuesta,
                defaults={"respuesta": respuesta_texto}
            )

    print("✔ Respuestas de encuestas generadas")
    print("\n🎉 TODO LISTO — Los datos ya pueden verse en los gráficos del dashboard.")


if __name__ == "__main__":
    run()
