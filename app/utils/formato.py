"""Filtros de Jinja para mostrar datos en español.

strftime('%B') depende del idioma del servidor (en Windows sale "October"),
por eso los meses se escriben aquí.
"""

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)
MESES_CORTOS = (
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
)

# Valores que guarda el formulario académico -> como se muestran
NIVELES_ACADEMICOS = {
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
    app.add_template_filter(mes_anio)
    app.add_template_filter(nivel_academico)
