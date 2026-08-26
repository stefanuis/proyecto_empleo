from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    IntegerField,
    SelectField,
    DateField,
    TextAreaField,
    BooleanField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class experienciaItemForm(Form):
    """Formulario para registro de experiencia laboral"""

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    entidad = StringField(
        "Nombre de la entidad/empresa",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    area = StringField(
        "Área de trabajo",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    cargo = StringField(
        "Cargo desempeñado",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    actual = BooleanField(
        "Actualmente trabajo aquí",
        validators=[Optional()]
    )

    motivo = SelectField(
    "Nivel",
    choices=[
        ("renuncia", "Renuncia"),
        ("terminacion_contrato", "Terminación de contrato"),
        ("despido", "Despido"),
        ("mutuo_acuerdo", "Mutuo acuerdo"),
        ("motivos_personales", "Motivos personales"),
        ("otra", "Otra")
    ],
    validators=[
        DataRequired()
       ]
    )

    otro = StringField(
        "Otro detalle",
        validators=[
            Optional(),
            Length(max=250)
        ]
    )

    fecha_ingreso = DateField(
        "Fecha de ingreso",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    fecha_salida = DateField(
        "Fecha de salida",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    pais = StringField(
        "País",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    departamento = StringField(
        "Departamento",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    municipio = StringField(
        "Municipio",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    funciones_realizadas = TextAreaField(
        "Funciones realizadas",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    ruta_soporte = FileField(
        "Documento soporte",
        validators=[
            Optional(),
            FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                       'Solo se permiten archivos: PDF, JPG, PNG, DOC, DOCX')
        ]
    )
class experienciaForm(FlaskForm):

    Info_experiencia = FieldList(
    FormField(experienciaItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")

