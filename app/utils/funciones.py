"""Funciones del catálogo y coincidencia entre vacante y candidato.

La vacante define qué funciones exige (VacanteFuncion) y el candidato marca
las que domina en su Perfil profesional (PerfilFuncion). La coincidencia es
cuántas de las funciones de la vacante tiene el candidato.
"""

from app.extensions import db
from app.models.funcion_area import FuncionArea
from app.models.perfil_funcion import PerfilFuncion
from app.models.vacante_funcion import VacanteFuncion


def funciones_activas_por_area(area_aplicacion):
    return FuncionArea.query.filter_by(
        area_aplicacion=area_aplicacion,
        activa=True,
    ).order_by(FuncionArea.nombre.asc()).all()


def funciones_de_vacante(id_vacante):
    return FuncionArea.query.join(
        VacanteFuncion,
        VacanteFuncion.id_funcion == FuncionArea.id,
    ).filter(
        VacanteFuncion.id_vacante == id_vacante,
    ).order_by(FuncionArea.nombre.asc()).all()


def funciones_validas_para_area(area_aplicacion, ids_enviados):
    """Valida los ids de funciones enviados en un formulario.

    Devuelve (funciones, error). Las funciones deben estar activas y
    pertenecer al área de aplicación indicada.
    """
    ids_funcion = set()
    for valor in ids_enviados:
        try:
            id_funcion = int(valor)
        except (TypeError, ValueError):
            return [], "La selección de funciones contiene valores inválidos."
        if id_funcion > 0:
            ids_funcion.add(id_funcion)

    if not ids_funcion:
        return [], "Selecciona al menos una función del cargo."

    funciones = FuncionArea.query.filter(
        FuncionArea.id.in_(ids_funcion),
        FuncionArea.area_aplicacion == area_aplicacion,
        FuncionArea.activa.is_(True),
    ).all()
    if len(funciones) != len(ids_funcion):
        return [], (
            "Cada función seleccionada debe estar activa y pertenecer "
            "al área de aplicación de la vacante."
        )
    return funciones, None


def guardar_funciones_vacante(id_vacante, funciones):
    """Reemplaza las funciones de la vacante (no hace commit)."""
    VacanteFuncion.query.filter_by(
        id_vacante=id_vacante
    ).delete(synchronize_session=False)
    for funcion in funciones:
        db.session.add(VacanteFuncion(id_vacante=id_vacante, id_funcion=funcion.id))


def funciones_de_candidatos(ids_usuario, ids_funciones):
    """{id_usuario: ids de `ids_funciones` que el candidato tiene}."""
    resultado = {id_usuario: set() for id_usuario in ids_usuario}
    if not resultado or not ids_funciones:
        return resultado

    filas = db.session.query(
        PerfilFuncion.id_usuario,
        PerfilFuncion.id_funcion,
    ).filter(
        PerfilFuncion.id_usuario.in_(list(resultado)),
        PerfilFuncion.id_funcion.in_(list(ids_funciones)),
    ).all()
    for id_usuario, id_funcion in filas:
        resultado[id_usuario].add(id_funcion)
    return resultado


def resumen_coincidencia(funciones_vacante, ids_candidato):
    """Resumen listo para mostrar: cuántas cumple, cuáles y cuáles le faltan."""
    total = len(funciones_vacante)
    cumplidas = [f for f in funciones_vacante if f.id in ids_candidato]
    faltantes = [f for f in funciones_vacante if f.id not in ids_candidato]
    return {
        "total": total,
        "cantidad": len(cumplidas),
        "porcentaje": round(len(cumplidas) * 100 / total) if total else 0,
        "cumplidas": cumplidas,
        "faltantes": faltantes,
    }


def coincidencias_por_vacante(id_usuario, ids_vacante):
    """{id_vacante: (funciones que cumple, funciones de la vacante)}.

    Solo incluye vacantes que tienen funciones definidas.
    """
    ids_vacante = list(ids_vacante)
    if not ids_vacante:
        return {}

    ids_candidato = {
        id_funcion
        for (id_funcion,) in db.session.query(PerfilFuncion.id_funcion).filter(
            PerfilFuncion.id_usuario == id_usuario
        ).all()
    }
    resultado = {}
    for id_vacante, id_funcion in db.session.query(
        VacanteFuncion.id_vacante,
        VacanteFuncion.id_funcion,
    ).filter(VacanteFuncion.id_vacante.in_(ids_vacante)).all():
        cumple, total = resultado.get(id_vacante, (0, 0))
        resultado[id_vacante] = (cumple + (id_funcion in ids_candidato), total + 1)
    return resultado


def coincidencia_candidato(id_usuario, id_vacante):
    funciones_vacante = funciones_de_vacante(id_vacante)
    ids_candidato = funciones_de_candidatos(
        [id_usuario], [f.id for f in funciones_vacante]
    )[id_usuario]
    return resumen_coincidencia(funciones_vacante, ids_candidato)
