# app/utils/perfil.py

from app.usuario.constantes import NOMBRES_PASO, PASOS_seguimiento
from app.models.personal import Personal
from datetime import date
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


RANKING_NIVEL = {
    'Bachillerato': 1,
    'tecnico': 2,
    'tecnologo': 3,
    'universitario': 4,
    'especializacion': 5,
    'maestria': 6,
    'doctorado': 7,
}


def obtener_nivel_mas_alto(id_usuario):
    registros = Info_academica.query.filter(
        Info_academica.id_usuario == id_usuario,
        Info_academica.estado == 'finalizado'
    ).all()

    if not registros:
        return None

    registro_mas_alto = max(registros, key=lambda r: RANKING_NIVEL.get(r.nivel, 0))
    return registro_mas_alto.nivel


def obtener_experiencia_total(id_usuario):
    registros = Experiencia.query.filter_by(id_usuario=id_usuario).all()
    if not registros:
        return 0
 
    total_dias = 0
    for exp in registros:
        if not exp.fecha_ingreso:
            continue
        fecha_fin = date.today() if exp.actual else exp.fecha_salida
        if not fecha_fin:
            continue
        total_dias += (fecha_fin - exp.fecha_ingreso).days
 
    return round(total_dias / 365.25, 1)
 
 
def formatear_experiencia(anos):
    """
    Convierte el número de años (float) a un texto legible:
    menos de 1 año se muestra en meses, de ahí en adelante en años.
    """
    if not anos:
        return '—'
 
    if anos < 1:
        meses = round(anos * 12)
        if meses == 0:
            return '—'
        return f"{meses} mes{'es' if meses != 1 else ''}"
 
    anos_redondeado = round(anos, 1)
    # Si el decimal es .0, lo mostramos como entero (ej. "3 años" en vez de "3.0 años")
    if anos_redondeado == int(anos_redondeado):
        anos_redondeado = int(anos_redondeado)
 
    return f"{anos_redondeado} año{'s' if anos_redondeado != 1 else ''}"