# generar_expediente.py
"""
Módulo para generar el PDF del expediente del postulante usando ReportLab.

PARTE 1: encabezado + información personal + contacto.
(Las secciones de académica, familiar y referencias se agregan después,
una vez validemos que esta parte se ve bien.)

Uso típico desde una ruta de Flask:

    from generar_expediente import generar_pdf_expediente

   
"""

import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable
)
from reportlab.lib.enums import TA_RIGHT


# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_titulo_doc = ParagraphStyle(
    'TituloDoc', parent=styles['Heading1'],
    fontSize=16, spaceAfter=4, textColor=colors.HexColor('#1a1a1a')
)

style_subtitulo = ParagraphStyle(
    'Subtitulo', parent=styles['Normal'],
    fontSize=10.5, textColor=colors.HexColor('#6b7280'), spaceAfter=0
)

style_nombre = ParagraphStyle(
    'Nombre', parent=styles['Heading2'],
    fontSize=15, spaceAfter=2, textColor=colors.HexColor('#1a1a1a')
)

style_h3 = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontSize=12.5, spaceBefore=14, spaceAfter=8,
    textColor=colors.HexColor('#1a1a1a')
)

style_label = ParagraphStyle(
    'Label', parent=styles['Normal'],
    fontSize=8.5, textColor=colors.HexColor('#6b7280'), spaceAfter=1
)

style_valor = ParagraphStyle(
    'Valor', parent=styles['Normal'],
    fontSize=10.5, textColor=colors.HexColor('#1a1a1a'), spaceAfter=6
)

style_badge = ParagraphStyle(
    'Badge', parent=styles['Normal'],
    fontSize=10, alignment=TA_RIGHT, textColor=colors.white
)

# Colores de los badges de estado, igual que en tu HTML (badge-pink, badge-blue, etc.)
COLOR_ESTADO = {
    'postulado':  colors.HexColor('#e91e63'),
    'revision':   colors.HexColor('#3b82f6'),
    'entrevista': colors.HexColor('#f97316'),
    'contratado': colors.HexColor('#22c55e'),
    'rechazado':  colors.HexColor('#ef4444'),
}
ETIQUETA_ESTADO = {
    'postulado':  'Postulado',
    'revision':   'En revisión',
    'entrevista': 'Entrevista',
    'contratado': 'Contratado',
    'rechazado':  'Rechazado',
}


def _dato(label, valor):
    """Devuelve una pareja (label pequeño + valor) como par de Paragraphs."""
    valor_txt = valor if valor not in (None, '', 'None') else '—'
    return [
        Paragraph(label, style_label),
        Paragraph(str(valor_txt), style_valor),
    ]


def _fila_datos(pares, col_widths=None):
    """
    Arma una fila de 2 columnas de datos (como tu .form-grid de 2 columnas).
    `pares` es una lista de tuplas (label, valor). Si son impares, la última
    queda sola.
    """
    filas = []
    for i in range(0, len(pares), 2):
        izq = _dato(*pares[i])
        der = _dato(*pares[i + 1]) if i + 1 < len(pares) else ['', '']
        filas.append([izq[0], der[0]])
        filas.append([izq[1], der[1]])

    tabla = Table(filas, colWidths=col_widths or [8.5 * cm, 8.5 * cm])
    tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    return tabla


def _fecha(valor):
    """Formatea una fecha tipo datetime a 'dd Mon YYYY', o '—' si no hay."""
    if not valor:
        return '—'
    try:
        return valor.strftime('%d %b %Y')
    except AttributeError:
        return str(valor)

def generar_pdf_expediente(personal, vacante, post, contacto=None, academica=None, familiar=None, referencias=None):
    """
    Genera el PDF del expediente completo:
    encabezado + personal + contacto + académica + familiar + referencias.
    Devuelve un BytesIO listo para enviar con send_file().
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )

    elementos = []

    # ---- Encabezado con logo (como tu .card-header) ----
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'logo_color.png')
    try:
        logo = Image(logo_path, width=2.8 * cm, height=1.4 * cm)
        logo.hAlign = 'RIGHT'
    except Exception:
        logo = Paragraph('', style_subtitulo)  # si no encuentra el logo, no truena

    tabla_header = Table(
        [[Paragraph('Hoja de vida del postulante', style_titulo_doc), logo]],
        colWidths=[13 * cm, 4 * cm]
    )
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tabla_header)
    elementos.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e5e9'), spaceBefore=8, spaceAfter=14))

    # ---- Nombre + vacante + badge de estado ----
    nombre_completo = f"{personal.nombres} {personal.apellidos}"
    texto_vacante = f"Postuló a: {vacante.titulo}"
    estado = getattr(post, 'estado', None)
    color_estado = COLOR_ESTADO.get(estado, colors.HexColor('#9ca3af'))
    etiqueta_estado = ETIQUETA_ESTADO.get(estado, estado or '—')

    badge = Table([[Paragraph(etiqueta_estado, style_badge)]], colWidths=[3.2 * cm])
    badge.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color_estado),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))

    bloque_nombre = [
        Paragraph(nombre_completo, style_nombre),
        Paragraph(texto_vacante, style_subtitulo),
    ]
    tabla_nombre_badge = Table(
        [[bloque_nombre, badge]], colWidths=[13 * cm, 4 * cm]
    )
    tabla_nombre_badge.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tabla_nombre_badge)
    elementos.append(Spacer(1, 10))

    # ---- Información personal ----
    elementos.append(Paragraph('Información personal', style_h3))
    documento = f"{personal.tipo_doc or ''} {personal.num_doc or ''}".strip()
    ubicacion = ", ".join(filter(None, [
        personal.direccion, personal.barrio, personal.municipio, personal.departamento
    ])) or '—'
    if getattr(personal, 'vive_rural', None) == 'si':
        ubicacion += ' (zona rural)'

    pares_personal = [
        ('Documento', documento or '—'),
        ('Fecha de expedición', _fecha(personal.fecha_exp_doc)),
        ('Fecha de nacimiento', _fecha(personal.fecha_nacimiento)),
        ('Género', personal.genero),
        ('Grupo étnico', personal.grupo_etnico),
        ('Nacionalidad', personal.nacionalidad),
        ('Estado civil', personal.estado_civil),
        ('Personas a cargo', personal.personas_cargo),
    ]
    elementos.append(_fila_datos(pares_personal))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph('Ubicación', style_label))
    elementos.append(Paragraph(ubicacion, style_valor))

    if getattr(personal, 'ruta_foto_doc', None):
        elementos.append(Paragraph(
            'Documento de identidad: (archivo adjunto disponible en el sistema)',
            style_valor
        ))

    # ---- Contacto ----
    elementos.append(Paragraph('Contacto', style_h3))
    pares_contacto = [
        ('Correo', personal.email),
        ('Celular', personal.num_cel),
        ('Celular alterno', personal.num_cel_dos),
    ]
    elementos.append(_fila_datos(pares_contacto))

    if contacto:
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph('Contacto de emergencia', style_label))
        nombre_contacto = f"{contacto.nombre} {contacto.apellido} ({contacto.parentesco or '—'})"
        pares_emergencia = [
            ('Nombre', nombre_contacto),
            ('Teléfono', contacto.tel),
            ('Núm. residencia', contacto.num_residencia),
        ]
        elementos.append(_fila_datos(pares_emergencia))

    # ---- Información académica ----
    elementos.append(Paragraph('Información académica', style_h3))
    if academica:
        for est in academica:
            titulo = est.titulo or est.nivel or '—'
            estado_est = getattr(est, 'estado', None) or '—'

            fila_titulo = Table(
                [[Paragraph(f"<b>{titulo}</b>", style_valor),
                  Paragraph(estado_est, style_label)]],
                colWidths=[13.5 * cm, 3.5 * cm]
            )
            fila_titulo.setStyle(TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elementos.append(fila_titulo)

            institucion = f"{est.institucion or '—'} — {est.pais_institucion or '—'}"
            elementos.append(Paragraph(institucion, style_valor))

            detalle = (
                f"Nivel: {est.nivel or '—'} · Área: {est.area or '—'} · "
                f"Finalización: {est.mes_finalizacion or '—'}/{est.anno_finalizacion or '—'} · "
                f"Intensidad: {est.intensidad_horaria or '—'}h"
            )
            if getattr(est, 'convalidacion', False):
                detalle += " · Convalidado"
            elementos.append(Paragraph(detalle, style_label))

            if getattr(est, 'ruta_soporte', None):
                elementos.append(Paragraph(
                    'Soporte: (archivo adjunto disponible en el sistema)', style_label
                ))

            elementos.append(Spacer(1, 10))
    else:
        elementos.append(Paragraph('No registró información académica.', style_label))

    # ---- Información familiar ----
    elementos.append(Paragraph('Información familiar', style_h3))
    if familiar:
        pares_familiar = [
            ('Personas en el hogar', familiar.personas_casa),
            ('Dependen económicamente', familiar.dependen_eco),
        ]
        elementos.append(_fila_datos(pares_familiar))
    else:
        elementos.append(Paragraph('No registró información familiar.', style_label))

    elementos.append(Spacer(1, 10))

    # ---- Referencias ----
    elementos.append(Paragraph('Referencias', style_h3))
    if referencias:
        encabezados = ['Nombre', 'Parentesco', 'Empresa', 'Teléfono', 'Ciudad', 'Autoriza']
        filas = [encabezados]

        for ref in referencias:
            nombre_ref = f"{ref.nombres} {ref.apellidos}"
            autoriza = 'Sí' if getattr(ref, 'autoriza', None) == 'si' else 'No'
            filas.append([
                nombre_ref,
                ref.parentesco or '—',
                ref.empresa or '—',
                ref.telefono or '—',
                ref.ciudad or '—',
                autoriza,
            ])

        tabla_referencias = Table(
            filas,
            colWidths=[4 * cm, 2.5 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 2 * cm]
        )
        tabla_referencias.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabla_referencias)
    else:
        elementos.append(Paragraph('No registró referencias.', style_label))

    doc.build(elementos)
    buffer.seek(0)
    return buffer