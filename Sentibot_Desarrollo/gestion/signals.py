from django.apps import apps
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def crear_roles_y_permisos(sender, **kwargs):
    roles = ['Alumno', 'Docente', 'Psicóloga', 'Admin']
    for rol in roles:
        Group.objects.get_or_create(name=rol)

    # Modelos de tu app
    app_label = 'gestion'
    Sesion = apps.get_model(app_label, 'Sesion')
    Actividad = apps.get_model(app_label, 'Actividad')
    Reporte = apps.get_model(app_label, 'Reporte')
    Encuesta = apps.get_model(app_label, 'EncuestaSatisfaccion')
    DocenteArea = apps.get_model(app_label, 'DocenteArea')
    User = apps.get_model('auth', 'User')

    # Crear permisos
    permisos = [
        # Alumno
        ('ver_inicio', 'Puede ver inicio', User),
        ('ver_perfil', 'Puede ver su perfil', User),
        ('ver_actividades', 'Puede ver actividades recomendadas', Actividad),
        ('reservar_cita', 'Puede reservar cita', Sesion),
        ('ver_historial_citas', 'Puede ver historial de citas', Sesion),

        # Psicóloga
        ('gestionar_alumnos', 'Puede gestionar alumnos', User),
        ('ver_lista_alumnos', 'Puede ver lista de alumnos', User),
        ('ver_estadisticas_alumnos', 'Puede ver estadísticas de alumnos', Sesion),
        ('gestionar_actividades', 'Puede gestionar actividades', Actividad),
        ('gestionar_reportes', 'Puede generar reportes', Reporte),
        ('gestionar_escuelas', 'Puede gestionar escuelas', DocenteArea),
        ('gestionar_recomendaciones', 'Puede gestionar recomendaciones', Actividad),
        ('integrar_api_citas', 'Puede integrar API de citas', Sesion),

        # Docente
        ('ver_vista_docente', 'Puede ver vista docente', User),
        ('ver_vista_escuela', 'Puede ver vista escuela', DocenteArea),
        ('ver_recomendaciones', 'Puede ver recomendaciones', Actividad),
        ('ver_graficos', 'Puede ver gráficos de estadísticas', Sesion),
    ]

    for codename, nombre, modelo in permisos:
        content_type = ContentType.objects.get_for_model(modelo)
        Permission.objects.get_or_create(codename=codename, name=nombre, content_type=content_type)

    # Asignar permisos a los grupos
    alumno_group = Group.objects.get(name='Alumno')
    psicologa_group = Group.objects.get(name='Psicóloga')
    docente_group = Group.objects.get(name='Docente')
    admin_group = Group.objects.get(name='Admin')

    # Alumno
    alumno_group.permissions.add(
        Permission.objects.get(codename='ver_inicio'),
        Permission.objects.get(codename='ver_perfil'),
        Permission.objects.get(codename='ver_actividades'),
        Permission.objects.get(codename='reservar_cita'),
        Permission.objects.get(codename='ver_historial_citas'),
    )

    # Psicóloga
    psicologa_group.permissions.add(
        Permission.objects.get(codename='ver_inicio'),
        Permission.objects.get(codename='gestionar_alumnos'),
        Permission.objects.get(codename='ver_lista_alumnos'),
        Permission.objects.get(codename='ver_estadisticas_alumnos'),
        Permission.objects.get(codename='gestionar_actividades'),
        Permission.objects.get(codename='gestionar_reportes'),
        Permission.objects.get(codename='gestionar_escuelas'),
        Permission.objects.get(codename='gestionar_recomendaciones'),
        Permission.objects.get(codename='integrar_api_citas'),
    )

    # Docente
    docente_group.permissions.add(
        Permission.objects.get(codename='ver_vista_docente'),
        Permission.objects.get(codename='ver_vista_escuela'),
        Permission.objects.get(codename='ver_recomendaciones'),
        Permission.objects.get(codename='ver_graficos'),
    )

    # Admin
    admin_group.permissions.add(*Permission.objects.all())

# Conectar señal
post_migrate.connect(crear_roles_y_permisos)
