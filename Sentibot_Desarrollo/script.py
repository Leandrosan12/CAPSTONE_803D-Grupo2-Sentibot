# -----------------------------
# IMPORTS
# -----------------------------
from gestion.models import Escuela, Rol, Emocion

# -----------------------------
# ESCUELAS
# -----------------------------
escuelas = [
    "Escuela de Administración y Negocios",
    "Escuela de Comunicación",
    "Escuela de Construcción",
    "Escuela de Diseño",
    "Escuela de Gastronomía",
    "Escuela de Informática y Telecomunicaciones",
    "Escuela de Ingeniería y Recursos Naturales",
    "Escuela de Salud y Bienestar",
    "Escuela de Turismo y Hospitalidad",
]

for nombre in escuelas:
    Escuela.objects.get_or_create(nombre=nombre)

print("✅ Escuelas cargadas correctamente.")

# -----------------------------
# ROLES
# -----------------------------
roles = [
    {"nombre": "Administrador", "descripcion": "Usuario con todos los permisos"},
    {"nombre": "Psicóloga", "descripcion": "Usuario con permisos de psicóloga"},
    {"nombre": "Profesor", "descripcion": "Usuario con permisos de docente"},
    {"nombre": "Alumno", "descripcion": "Usuario que participa en encuestas y actividades"},
    {"nombre": "Otro", "descripcion": "Rol genérico para otros tipos de usuario"},
]

for r in roles:
    Rol.objects.get_or_create(nombre=r["nombre"], defaults={"descripcion": r["descripcion"]})

print("✅ Roles cargados correctamente.")

# -----------------------------
# EMOCIONES
# -----------------------------
emociones = [
    {"nombre_emocion": "Alegría", "descripcion": "Emoción de alegría y satisfacción"},
    {"nombre_emocion": "Tristeza", "descripcion": "Emoción de desánimo o tristeza"},
    {"nombre_emocion": "Miedo", "descripcion": "Emoción de miedo"},
    {"nombre_emocion": "Enojo", "descripcion": "Emoción de irritación o enojo"},
    {"nombre_emocion": "Neutral", "descripcion": "Emoción sin cambios significativos"},
]

for e in emociones:
    Emocion.objects.get_or_create(nombre_emocion=e["nombre_emocion"], defaults={"descripcion": e["descripcion"]})

print("✅ Emociones cargadas correctamente.")
