from app.models.perfil_profesional import PerfilProfesional
from app.usuario.constantes import AREAS_AFINES, VALIDAR_NIVEL_ACADEMICO
from app.utils.perfil import obtener_nivel_mas_alto


def _rango_nivel(nivel):
    niveles = {
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
    return niveles.get((nivel or "").strip().casefold())


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

    if VALIDAR_NIVEL_ACADEMICO and vacante.nivel_academico:
        nivel_candidato = obtener_nivel_mas_alto(usuario_id)
        rango_candidato = _rango_nivel(nivel_candidato)
        rango_requerido = _rango_nivel(vacante.nivel_academico)
        if (
            rango_candidato is None
            or rango_requerido is None
            or rango_candidato < rango_requerido
        ):
            nivel_mostrado = nivel_candidato or "sin nivel finalizado"
            requisitos_no_cumplidos.append(
                f"La vacante requiere {vacante.nivel_academico}; "
                f"tu nivel finalizado más alto es {nivel_mostrado}."
            )

    return requisitos_no_cumplidos
