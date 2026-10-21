"""Filtros de Jinja para mostrar datos en español.

strftime('%B') depende del idioma del servidor (en Windows sale "October"),
por eso los meses se escriben aquí.
"""

from datetime import date

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MESES_CORTOS = (
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
)

# Valores que guarda el formulario académico -> como se muestran
NIVELES_ACADEMICOS = {
    "primaria": "Primaria",
    "bachillerato": "Bachillerato",
    "tecnico": "Técnico",
    "tecnologo": "Tecnólogo",
    "universitario": "Universitario",
    "especializacion": "Especialización",
    "maestria": "Maestría",
    "doctorado": "Doctorado",
}


def fecha_larga(valor):
    """11 de octubre de 2026"""
    if not valor:
        return "—"
    return f"{valor.day} de {MESES[valor.month - 1]} de {valor.year}"


# Estado de un estudio (formulario académico) -> como se muestra
ESTADOS_ACADEMICOS = {
    "en_curso": "En curso",
    "finalizado": "Finalizado",
    "incompleto": "Incompleto",
    "aplazado": "Aplazado",
    "cancelado": "Cancelado",
}


def estado_academico(valor):
    if not valor:
        return "—"
    return ESTADOS_ACADEMICOS.get(valor.strip().lower(), valor)


def edad(fecha_nacimiento, hoy=None):
    """Años cumplidos; None si no hay fecha."""
    if not fecha_nacimiento:
        return None
    hoy = hoy or date.today()
    if hasattr(fecha_nacimiento, "date"):
        fecha_nacimiento = fecha_nacimiento.date()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def fecha_con_dia(valor):
    """viernes 24 de octubre de 2026"""
    if not valor:
        return "—"
    return f"{DIAS[valor.weekday()]} {fecha_larga(valor)}"


def hora_12(valor):
    """9:30 a. m."""
    if not valor:
        return "—"
    sufijo = "a. m." if valor.hour < 12 else "p. m."
    return f"{(valor.hour % 12) or 12}:{valor.minute:02d} {sufijo}"


def fecha_corta(valor):
    """11 oct 2026"""
    if not valor:
        return "—"
    return f"{valor.day:02d} {MESES_CORTOS[valor.month - 1]} {valor.year}"


def mes_anio(valor):
    """oct 2026"""
    if not valor:
        return "—"
    return f"{MESES_CORTOS[valor.month - 1]} {valor.year}"


def nivel_academico(valor):
    if not valor:
        return "—"
    return NIVELES_ACADEMICOS.get(valor.strip().lower(), valor)


def registrar_filtros(app):
    app.add_template_filter(fecha_larga)
    app.add_template_filter(fecha_corta)
    app.add_template_filter(fecha_con_dia)
    app.add_template_filter(estado_academico)
    app.add_template_filter(edad)
    app.add_template_filter(hora_12)
    app.add_template_filter(mes_anio)
    app.add_template_filter(nivel_academico)
