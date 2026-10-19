
#eso me ayudara a saber por donde voy
PASOS_seguimiento = [
    "personal",
    "perfil_profesional",
    "academica",
    "experiencia",
    "cursos",
    "referencias",
    "referencias_personales",  
    "discapacidades",
    "documentos",
]

TOTAL_PASOS = len(PASOS_seguimiento)

# Ejemplo: {"Medicina": ["Enfermería"]} permite Enfermería para vacantes de Medicina.
AREAS_AFINES = {}

VALIDAR_NIVEL_ACADEMICO = False

REGLAS_PASO = {
    "personal": {
        "tipo": "registros",
        "minimo": 1,
    },
    "perfil_profesional": {
        "tipo": "perfil_profesional",
        "minimo": 1,
    },
    "academica": {
        "tipo": "registros",
        "minimo": 1,
        "mensaje": "Agrega al menos un registro de formación académica.",
    },
    "experiencia": {
        "tipo": "registros_o_declaracion",
        "minimo": 1,
        "campo_declaracion": "no_tengo_experiencia",
        "mensaje": (
            "Agrega al menos un registro de experiencia, o marca que no "
            "tienes experiencia laboral."
        ),
    },
    "cursos": {
        "tipo": "registros_o_declaracion",
        "minimo": 1,
        "campo_declaracion": "no_tengo_cursos",
        "mensaje": "Agrega al menos un curso, o marca que no tienes cursos.",
    },
    "referencias": {
        "tipo": "registros_o_declaracion",
        "minimo": 1,
        "campo_declaracion": "no_tengo_referencias",
        "mensaje": (
            "Agrega al menos una referencia laboral, o marca que no tienes "
            "referencias laborales."
        ),
    },
    "referencias_personales": {
        "tipo": "registros",
        "minimo": 1,
        "mensaje": "Agrega al menos una referencia personal.",
    },
    "discapacidades": {
        "tipo": "opcional",
    },
    "documentos": {
        "tipo": "registros",
        "minimo": 1,
    },
}

# Título corto de cada paso (se muestra en negrita y en el tooltip de la barra)
NOMBRES_PASO = {
    "personal": "Datos personales",
    "perfil_profesional": "Perfil profesional",
    "academica": "Formación académica",
    "experiencia": "Experiencia laboral",
    "cursos": "Cursos",
    "referencias": "Referencias laborales",
    "referencias_personales": "Referencias personales",
    "discapacidades": "Discapacidades",
    "documentos": "Documentos",
}

# Descripción breve de cada paso (una frase corta)
DESCRIPCIONES_PASO = {
    "personal": "Información básica de identificación del candidato.",
    "perfil_profesional": "Área de aplicación, descripción y funciones que dominas.",
    "academica": "Nivel educativo, institución, título y año de graduación.",
    "experiencia": "Empresas, cargos desempeñados y funciones.",
    "cursos": "Diplomados, certificaciones y formación complementaria.",
    "referencias": "Contactos que puedan validar tu desempeño laboral.",
     "referencias_personales": "Contactos personales que puedan dar referencias tuyas.",
    "discapacidades": "Condición y ajustes razonables, en caso de aplicar.",
    "documentos": "Hoja de vida, cédula, diplomas y demás soportes.",
}