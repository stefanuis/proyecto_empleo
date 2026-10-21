DISCAPACIDAD_CATEGORIAS = [
    ("", "Seleccione"),
    ("Física", "Física"),
    ("Auditiva", "Auditiva"),
    ("Visual", "Visual"),
    ("Sordoceguera", "Sordoceguera"),
    ("Intelectual", "Intelectual"),
    ("Psicosocial", "Psicosocial"),
    ("Múltiple", "Múltiple"),
]

DISCAPACIDAD_CATEGORIAS_LEGADAS = ("Sensorial", "Cognitiva", "Otra")

GRUPO_ETNICO_OPCIONES = [
    ("", "Seleccione"),
    ("Indígena", "Indígena"),
    ("Gitano o Rrom", "Gitano o Rrom"),
    ("Raizal", "Raizal"),
    ("Palenquero", "Palenquero"),
    ("Afrocolombiano", "Afrocolombiano"),
    ("Ninguno", "Ninguno"),
    ("Prefiero no responder", "Prefiero no responder"),
]

# Estados de una postulación: valor guardado -> etiqueta que se muestra
ESTADOS_POSTULACION = {
    "postulado": "Postulado",
    "revision": "En revisión",
    "entrevista": "Entrevista",
    "contratado": "Contratado",
    "rechazado": "Rechazado",
    "retirada": "Retirada",
}

# Estados a los que el candidato puede ser avisado por correo al cambiar.
# "rechazado" tiene su propio correo (botón en el expediente) y la
# entrevista se avisa con la citación.
MENSAJES_CAMBIO_ESTADO = {
    "revision": {
        "asunto": "Tu postulación está en revisión",
        "titulo": "Tu hoja de vida está en revisión",
        "mensaje": (
            "Nuestro equipo de Gestión Humana está revisando tu perfil para la "
            "vacante. Te avisaremos por este medio cuando haya novedades."
        ),
    },
    "entrevista": {
        "asunto": "Avanzaste a la etapa de entrevista",
        "titulo": "¡Avanzaste a la etapa de entrevista!",
        "mensaje": (
            "Tu perfil fue seleccionado para la etapa de entrevista. Pronto "
            "recibirás un correo con la fecha, la hora y el lugar."
        ),
    },
    "contratado": {
        "asunto": "¡Felicitaciones! Fuiste seleccionado",
        "titulo": "¡Felicitaciones, fuiste seleccionado!",
        "mensaje": (
            "Fuiste seleccionado para la vacante. El equipo de Gestión Humana "
            "se comunicará contigo para los siguientes pasos."
        ),
    },
}
