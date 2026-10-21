# app/utils/perfil.py

from app.usuario.constantes import (
    DOCUMENTOS_OBLIGATORIOS,
    NOMBRES_PASO,
    PASOS_seguimiento,
    REGLAS_PASO,
)
from app.models.personal import Personal
from datetime import date, datetime
from app.models.academica import Info_academica
from app.models.experiencia import Experiencia
from app.models.cursos import Cursos
from app.models.referencias import Referencias
from app.models.referencias_personales import ReferenciasPersonales
from app.models.docs import OtrosDocumentos
from app.models.perfil_profesional import PerfilProfesional
from app.models.perfil_funcion import PerfilFuncion
from app.models.paso_omitido import PasoOmitido


MODELOS_POR_PASO = {
    "personal": Personal,
    "academica": Info_academica,
    "experiencia": Experiencia,
    "cursos": Cursos,
    "referencias": Referencias,
    "referencias_personales": ReferenciasPersonales,
    "documentos": OtrosDocumentos,
}


def existe_registro(modelo, id_usuario):
    """Devuelve True si el usuario ya tiene al menos un registro en ese modelo."""
    return modelo.query.filter_by(id_usuario=id_usuario).first() is not None


def perfil_profesional_completo(id_usuario):
    perfil = PerfilProfesional.query.filter_by(id_usuario=id_usuario).first()
    if not perfil or not (perfil.area_aplicacion or "").strip():
        return False

    return PerfilFuncion.query.filter_by(id_usuario=id_usuario).first() is not None


def documentos_obligatorios_faltantes(id_usuario):
    """Tipos de DOCUMENTOS_OBLIGATORIOS que el usuario aún no ha subido."""
    tipos_cargados = {
        tipo
        for (tipo,) in OtrosDocumentos.query.with_entities(
            OtrosDocumentos.tipo
        ).filter_by(id_usuario=id_usuario).all()
    }
    return [tipo for tipo in DOCUMENTOS_OBLIGATORIOS if tipo not in tipos_cargados]


def calcular_completitud_perfil(id_usuario):
    secciones = {}
    for paso, regla in REGLAS_PASO.items():
        tipo = regla["tipo"]
        if tipo == "opcional":
            secciones[paso] = True
        elif tipo == "perfil_profesional":
            secciones[paso] = perfil_profesional_completo(id_usuario)
        elif tipo == "documentos_obligatorios":
            secciones[paso] = not documentos_obligatorios_faltantes(id_usuario)
        else:
            modelo = MODELOS_POR_PASO[paso]
            cantidad_registros = modelo.query.filter_by(
                id_usuario=id_usuario
            ).count()
            tiene_registros = cantidad_registros >= regla.get("minimo", 1)
            if tipo == "registros_o_declaracion":
                tiene_declaracion = PasoOmitido.query.filter_by(
                    id_usuario=id_usuario,
                    paso=paso,
                ).first() is not None
                secciones[paso] = tiene_registros or tiene_declaracion
            else:
                secciones[paso] = tiene_registros

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


DIAS_POR_ANIO = 365.25


def _como_fecha(valor):
    return valor.date() if isinstance(valor, datetime) else valor


def _dias_sin_solapar(registros, hoy=None):
    """Días de experiencia reales de una lista de registros de Experiencia.

    - Un trabajo actual cuenta hasta hoy.
    - Se ignoran registros sin fechas o con salida anterior al ingreso.
    - Los periodos que se cruzan se unen, para no contar dos veces el
      mismo tiempo (por ejemplo, dos trabajos simultáneos).
    """
    hoy = hoy or date.today()
    periodos = []
    for exp in registros:
        inicio = _como_fecha(exp.fecha_ingreso)
        fin = hoy if exp.actual else _como_fecha(exp.fecha_salida)
        if not inicio or not fin:
            continue
        fin = min(fin, hoy)
        if fin < inicio:
            continue
        periodos.append((inicio, fin))

    total_dias = 0
    tramo_inicio = tramo_fin = None
    for inicio, fin in sorted(periodos):
        if tramo_fin is None or inicio > tramo_fin:
            if tramo_fin is not None:
                total_dias += (tramo_fin - tramo_inicio).days
            tramo_inicio, tramo_fin = inicio, fin
        else:
            tramo_fin = max(tramo_fin, fin)
    if tramo_fin is not None:
        total_dias += (tramo_fin - tramo_inicio).days

    return total_dias


def dias_experiencia_por_usuario(ids_usuario):
    """{id_usuario: días de experiencia} con una sola consulta."""
    ids_usuario = list(ids_usuario)
    registros_por_usuario = {id_usuario: [] for id_usuario in ids_usuario}
    if ids_usuario:
        for exp in Experiencia.query.filter(
            Experiencia.id_usuario.in_(ids_usuario)
        ).all():
            registros_por_usuario[exp.id_usuario].append(exp)
    return {
        id_usuario: _dias_sin_solapar(registros)
        for id_usuario, registros in registros_por_usuario.items()
    }


def obtener_experiencia_total(id_usuario):
    """Años de experiencia (con un decimal), para mostrar."""
    registros = Experiencia.query.filter_by(id_usuario=id_usuario).all()
    return round(_dias_sin_solapar(registros) / DIAS_POR_ANIO, 1)


def formatear_experiencia(anos):
    """
    Convierte el número de años (float) a un texto legible:
    menos de 1 año se muestra en meses, de ahí en adelante en años.
    """
    if not anos or anos <= 0:
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