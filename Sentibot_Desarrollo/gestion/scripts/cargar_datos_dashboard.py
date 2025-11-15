import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from gestion.models import (
    Usuario, Escuela, EmotionSession,
    Encuesta, RespuestaEncuesta
)


def run():
    print("🌱 Insertando datos REALES para el dashboard...")

    # ============================
    # 1. CREAR ESCUELAS
    # ============================
    escuelas = []
    nombres_escuelas = ["Escuela A", "Escuela B", "Escuela C"]

    for nombre in nombres_escuelas:
        escuela, _ = Escuela.objects.get_or_create(
            nombre=nombre,
            sede="Melipilla"
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
    # 3. CREAR SESIONES EMOCIONALES
    # ============================
    emociones = ["feliz", "triste", "neutral", "enojado", "sorprendido", "sinreconocer"]

    for _ in range(80):
        user = random.choice(usuarios)

        # valores aleatorios por emoción
        emocion_values = {
            f"{e}_seg": random.randint(5, 120)
        
        }

        EmotionSession.objects.create(
            user=user,
            **emocion_values
        )

    print("✔ 80 sesiones emocionales insertadas")

    # ============================
    # 4. CREAR ENCUESTAS + RESPUESTAS
    # ============================
    encuestas = []
    nombres_encuestas = ["Encuesta satisfacción", "Encuesta clase", "Encuesta emoción"]

    for n in nombres_encuestas:
        e, _ = Encuesta.objects.get_or_create(
            nombre=n,
            tipo="si/no",
            descripcion="Encuesta generada automáticamente"
        )
        encuestas.append(e)

    # crear respuestas para las escuelas
    for user in usuarios:
        for encuesta in encuestas:
            respuesta_texto = random.choice(["si", "no"])

            RespuestaEncuesta.objects.create(
                usuario=user,
                encuesta=encuesta,
                respuesta=respuesta_texto
            )

    print("✔ Respuestas de encuestas generadas")

    print("\n🎉 TODO LISTO — Los datos ya pueden verse en los gráficos del dashboard.")


if __name__ == "__main__":
    run()
