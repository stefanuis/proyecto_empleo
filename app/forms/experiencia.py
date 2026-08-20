from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    DateField,
    SubmitField,
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

    motivo = StringField(
        "Motivo de salida",
        validators=[
            Optional(),
            Length(max=100)
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

