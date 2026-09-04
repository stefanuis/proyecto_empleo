from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    BooleanField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField,
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)

class InforAcademicaItemForm(Form):
    """Formulario para información académica del usuario"""
    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    nivel = SelectField(
    "Tipo de formación académica",
    choices=[
        ("Bachillerato", "Bachillerato"),
        ("tecnico", "Técnico"),
        ("tecnologo", "Tecnólogo"),
        ("universitario", "Universitario"),
        ("especializacion", "Especialización"),
        ("maestria", "Maestría"),
        ("doctorado", "Doctorado")
    ],
    validators=[
        DataRequired()
    ]
)

    estado = SelectField(
    "Estado académico",
    choices=[
        ("en_curso", "En curso"),
        ("finalizado", "Finalizado"),
        ("incompleto", "Incompleto"),
        ("aplazado", "Aplazado"),
        ("cancelado", "Cancelado"),
    ],
    validators=[
        DataRequired()
    ]
)
    periodos_cursados = IntegerField(
        "Períodos cursados académicamente",
        validators=[
            Optional(),
            NumberRange(min=0)
        ]
    )

    #area = StringField(
    #    "Área académica",
    #    validators=[
    #        DataRequired(),
    #        Length(max=30)
    #    ]
    #)


    area = SelectField(
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


    titulo = StringField(
        "Título obtenido",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    institucion = StringField(
        "Institución educativa",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    pais_institucion = StringField(
        "País de la institución",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    convalidacion = BooleanField(
        "Convalidación",
        validators=[Optional()]
    )

    mes_finalizacion = IntegerField(
        "Mes de finalización",
        validators=[
            Optional(),
            NumberRange(min=1, max=12)
        ]
    )

    anno_finalizacion = IntegerField(
        "Año de finalización",
        validators=[
            Optional(),
            NumberRange(min=1950, max=2030)
        ]
    )

    intensidad_horaria = IntegerField(
        "Intensidad horaria",
        validators=[
            Optional(),
            NumberRange(min=0)
        ]
    )

    ruta_soporte = FileField(
        "Documento de soporte",
        validators=[
            Optional(),
            FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Solo se permiten archivos PDF, Word e imágenes')
        ]
    )



class InforAcademicaForm(FlaskForm):

    Info_academica = FieldList(
        FormField(InforAcademicaItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")