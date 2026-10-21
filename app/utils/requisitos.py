from sqlalchemy import false, func, or_

from app.models.perfil_profesional import PerfilProfesional
from app.models.vacante import Vacante
from app.usuario.constantes import AREAS_AFINES, VALIDAR_NIVEL_ACADEMICO
from app.utils.formato import nivel_academico
from app.utils.perfil import obtener_nivel_mas_alto


NIVELES_POR_RANGO = {
        "primaria": 0,
        "bachillerato": 1,
        "técnico": 2,
        "tecnico": 2,
        "tecnólogo": 3,
        "tecnologo": 3,
        "profesional universitario": 4,
        "universitario": 4,
        "especialización": 5,
        "especializacion": 5,
        "maestría": 6,
        "maestria": 6,
        "doctorado": 7,
}


def _rango_nivel(nivel):
    return NIVELES_POR_RANGO.get((nivel or "").strip().casefold())


def cumple_requisitos(usuario_id, vacante):
    requisitos_no_cumplidos = []
    perfil = PerfilProfesional.query.filter_by(id_usuario=usuario_id).first()
    area_candidato = perfil.area_aplicacion if perfil else None
    area_vacante = vacante.area_aplicacion

    if not area_candidato or not area_candidato.strip():
        requisitos_no_cumplidos.append(
            "Completa tu Perfil profesional antes de postularte."
        )
    elif area_vacante and area_vacante.strip() and area_candidato != area_vacante:
        areas_permitidas = AREAS_AFINES.get(area_vacante, ())
        if area_candidato not in areas_permitidas:
            requisitos_no_cumplidos.append(
                f"La vacante requiere el área {area_vacante}; "
                f"tu perfil indica {area_candidato}."
            )

    # Un nivel que no se reconoce en la vacante no bloquea a nadie
    rango_requerido = _rango_nivel(vacante.nivel_academico)
    if VALIDAR_NIVEL_ACADEMICO and rango_requerido is not None:
        nivel_candidato = obtener_nivel_mas_alto(usuario_id)
        rango_candidato = _rango_nivel(nivel_candidato)
        if rango_candidato is None or rango_candidato < rango_requerido:
            if nivel_candidato:
                detalle = (
                    "tu nivel finalizado más alto es "
                    f"{nivel_academico(nivel_candidato)}."
                )
            else:
                detalle = "aún no tienes estudios finalizados registrados."
            requisitos_no_cumplidos.append(
                f"La vacante requiere {vacante.nivel_academico} finalizado; "
                f"{detalle}"
            )
    return requisitos_no_cumplidos


def condiciones_vacantes_postulables(usuario_id):
    """Las mismas reglas de cumple_requisitos, como filtros SQL.

    Sirve para listar solo las vacantes a las que el candidato puede
    postularse sin perder la paginación en la base de datos.
    """
    perfil = PerfilProfesional.query.filter_by(id_usuario=usuario_id).first()
    area_candidato = (perfil.area_aplicacion or "").strip() if perfil else ""
    if not area_candidato:
        return [false()]

    areas_validas = [area_candidato] + [
        area_vacante
        for area_vacante, afines in AREAS_AFINES.items()
        if area_candidato in afines
    ]
    condiciones = [
        or_(
            Vacante.area_aplicacion.is_(None),
            func.trim(Vacante.area_aplicacion) == "",
            Vacante.area_aplicacion.in_(areas_validas),
        )
    ]

    if VALIDAR_NIVEL_ACADEMICO:
        rango_candidato = _rango_nivel(obtener_nivel_mas_alto(usuario_id))
        alcanzables = [
            nombre
            for nombre, rango in NIVELES_POR_RANGO.items()
            if rango_candidato is not None and rango <= rango_candidato
        ]
        nivel_vacante = func.lower(func.trim(Vacante.nivel_academico))
        condiciones.append(
            or_(
                Vacante.nivel_academico.is_(None),
                # Un nivel que no se reconoce no bloquea (igual que arriba)
                ~nivel_vacante.in_(list(NIVELES_POR_RANGO)),
                nivel_vacante.in_(alcanzables),
            )
        )

    return condiciones


def detalle_requisitos(usuario_id, vacante):
    """Cada requisito de la vacante frente al candidato, para mostrarlo.

    [{"nombre", "requerido", "candidato", "cumple"}]; usa las mismas reglas
    que cumple_requisitos (área afín y nivel finalizado igual o superior).
    """
    perfil = PerfilProfesional.query.filter_by(id_usuario=usuario_id).first()
    area_candidato = (perfil.area_aplicacion or "").strip() if perfil else ""
    area_vacante = (vacante.area_aplicacion or "").strip()
    detalle = []

    if area_vacante:
        detalle.append({
            "nombre": "Área de aplicación",
            "requerido": area_vacante,
            "candidato": area_candidato or "Sin perfil profesional",
            "cumple": bool(area_candidato) and (
                area_candidato == area_vacante
                or area_candidato in AREAS_AFINES.get(area_vacante, ())
            ),
        })

    rango_requerido = _rango_nivel(vacante.nivel_academico)
    if rango_requerido is not None:
        nivel_candidato = obtener_nivel_mas_alto(usuario_id)
        rango_candidato = _rango_nivel(nivel_candidato)
        detalle.append({
            "nombre": "Nivel académico finalizado",
            "requerido": vacante.nivel_academico,
            "candidato": nivel_academico(nivel_candidato) if nivel_candidato else "Sin estudios finalizados",
            "cumple": rango_candidato is not None and rango_candidato >= rango_requerido,
        })

    return detalle
