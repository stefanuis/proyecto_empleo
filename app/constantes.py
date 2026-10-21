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
    # Stock: el candidato gustó pero no se eligió; queda guardado para
    # sugerirlo en próximas vacantes de la misma área
    "stock": "En stock",
    "contratado": "Contratado",
    "rechazado": "Rechazado",
    "retirada": "Retirada",
}

# Lo que ve el candidato en "Mis postulaciones" (stock se le muestra como espera)
ESTADOS_POSTULACION_CANDIDATO = {**ESTADOS_POSTULACION, "stock": "En espera"}

# Estados a los que el candidato puede ser avisado por correo al cambiar.
# "rechazado" usa su propio correo (c_rechazo.html, ver _notificar_rechazo
# en admin/principal.py) y la entrevista se avisa con la citación.
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
    "stock": {
        "asunto": "Tu perfil quedó guardado para futuras vacantes",
        "titulo": "Tu perfil quedó guardado para futuras vacantes",
        "mensaje": (
            "En esta ocasión la vacante se cubrió con otra persona, pero tu perfil "
            "nos gustó. Lo guardamos para tenerte en cuenta en las próximas "
            "vacantes similares; no necesitas hacer nada por ahora."
        ),
    },
}

# Correo cuando una persona en stock se agrega a una vacante nueva
MENSAJE_DESDE_STOCK = {
    "asunto": "Te tenemos en cuenta para una nueva vacante",
    "titulo": "¡Te tenemos en cuenta para una nueva vacante!",
    "mensaje": (
        "Tu perfil estaba guardado en nuestro banco de candidatos y lo agregamos "
        "a esta vacante. Nuestro equipo de Gestión Humana lo está revisando y te "
        "avisaremos por este medio cuando haya novedades."
    ),
}
