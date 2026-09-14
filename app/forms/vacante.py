from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    TextAreaField,
    BooleanField,
    DateField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class VacanteForm(FlaskForm):
    """Formulario para registro de vacantes laborales"""

    titulo = StringField(
        "Título del puesto",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    
    area = SelectField(
         "Área/Departamento",
        choices=[
            ("", "Selecciona el area"),
            ("Asistencial", "Asistencial"),
            ("Administrativa", "Administrativa")
           
        ],
        validators=[DataRequired()]
    )

    descripcion = TextAreaField(
        "Descripción de la vacante",
        validators=[
            DataRequired(),
            Length(max=500)
        ]
    )

    requisito = TextAreaField(
        "Requisitos",
        validators=[
            DataRequired(),
            Length(max=500)
        ]
    )

    salario = StringField(
        "Información de salario",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    estado = SelectField(
        "Estado de la vacante",
        choices=[
            ("", "Selecciona un estado"),
            ("Activa", "Activa"),
            ("Cerrada", "Cerrada")
           
        ],
        validators=[DataRequired()]
    )

    
    fecha_publicacion = DateField(
        "Fecha de publicacion",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    fecha_cierre = DateField(
        "Fecha de cierre",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    area_aplicacion = SelectField(
        "Área de Aplicación",
        choices=[
            ("", "Selecciona area de tu conocimiento"),
            ("Administrativo", "Administrativo"),
            ("Admisiones", "Admisiones"),
            ("Archivo y Gestión Documental", "Archivo y Gestión Documental"),
            ("Auditoría en Salud", "Auditoría en Salud"),
            ("Calidad", "Calidad"),
            ("Contabilidad y Finanzas", "Contabilidad y Finanzas"),
            ("Enfermería", "Enfermería"),
            ("Facturación y Cartera", "Facturación y Cartera"),
            ("Farmacia", "Farmacia"),
            ("Fisioterapia y Rehabilitación", "Fisioterapia y Rehabilitación"),
            ("Gestión Humana", "Gestión Humana"),
            ("Imágenes Diagnósticas", "Imágenes Diagnósticas"),
            ("Ingeniería Biomédica", "Ingeniería Biomédica"),
            ("Infraestructura y Obras", "Infraestructura y Obras"),
            ("Instrumentación Quirúrgica", "Instrumentación Quirúrgica"),
            ("Investigación y Docencia", "Investigación y Docencia"),
            ("Jurídica", "Jurídica"),
            ("Laboratorio Clínico", "Laboratorio Clínico"),
            ("Logística", "Logística"),
            ("Mantenimiento", "Mantenimiento"),
            ("Medicina", "Medicina"),
            ("Mercadeo y Comunicaciones", "Mercadeo y Comunicaciones"),
            ("Nutrición", "Nutrición"),
            ("Odontología", "Odontología"),
            ("Psicología", "Psicología"),
            ("Seguridad del Paciente", "Seguridad del Paciente"),
            ("Seguridad Física", "Seguridad Física"),
            ("Seguridad y SST", "Seguridad y SST"),
            ("Servicios Generales", "Servicios Generales"),
            ("Servicio al Cliente", "Servicio al Cliente"),
            ("Sistemas - TI", "Sistemas - TI"),
            ("Trabajo Social", "Trabajo Social"),
        ],
        validators=[DataRequired()]
    )

    nivel_academico = SelectField(
        "Nivel Académico",
        choices=[
            ("", "Selecciona un nivel"),
            ("Primaria", "Primaria"),
            ("Bachillerato", "Bachillerato"),
            ("Técnico", "Técnico"),
            ("Tecnólogo", "Tecnólogo"),
            ("Profesional universitario", "Profesional universitario"),
            ("Especialización", "Especialización"),
            ("Maestría", "Maestría"),
            ("Doctorado", "Doctorado")
           
        ],
        validators=[DataRequired()]
    )

    
    requiere_video = BooleanField(
        "requiere video de presentacion",
        validators=[Optional()]
    )

    submit = SubmitField("Guardar vacante")
