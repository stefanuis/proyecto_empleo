# app/utils/perfil.py

from app.usuario.constantes import NOMBRES_PASO, PASOS_seguimiento
from app.models.personal import Personal
from app.models.contacto import Contacto
from app.models.familiar import Familiar
from app.models.academica import Info_academica
from app.models.experiencia import Experiencia
from app.models.cursos import Cursos
from app.models.competencias import Competencias
from app.models.referencias import Referencias
from app.models.referencias_personales import ReferenciasPersonales
from app.models.docs import OtrosDocumentos


def existe_registro(modelo, id_usuario):
    """Devuelve True si el usuario ya tiene al menos un registro en ese modelo."""
    return modelo.query.filter_by(id_usuario=id_usuario).first() is not None


def calcular_completitud_perfil(id_usuario):
    secciones = {
        "personal": existe_registro(Personal, id_usuario),
        "contacto": existe_registro(Contacto, id_usuario),
        "familiar": existe_registro(Familiar, id_usuario),
        "academica": existe_registro(Info_academica, id_usuario),
        "experiencia": existe_registro(Experiencia, id_usuario),
        "cursos": existe_registro(Cursos, id_usuario),
        "competencias": existe_registro(Competencias, id_usuario),
        "referencias": existe_registro(Referencias, id_usuario),
        "referencias_personales": existe_registro(ReferenciasPersonales, id_usuario),
        "discapacidades": True,
        "documentos": existe_registro(OtrosDocumentos, id_usuario),
    }

    total = len(secciones)
    completadas = sum(1 for esta_completa in secciones.values() if esta_completa)
    porcentaje = round((completadas / total) * 100)

    faltantes = [
        NOMBRES_PASO[clave]
        for clave, esta_completa in secciones.items()
        if not esta_completa
    ]

    # Primer paso faltante, respetando el ORDEN de PASOS_seguimiento
    primer_paso_faltante = next(
        (clave for clave in PASOS_seguimiento if not secciones.get(clave, True)),
        None  # None si ya completó todo
    )

    return {
        "porcentaje": porcentaje,
        "completadas": completadas,
        "total": total,
        "faltantes": faltantes,
        "secciones": secciones,
        "primer_paso_faltante": primer_paso_faltante,
    }