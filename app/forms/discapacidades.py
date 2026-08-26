from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    TextAreaField,
    FieldList,
    FormField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class discapacidadItemForm(Form):
    """Formulario para registro de discapacidades"""

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    categoria = SelectField(
        "Categoría de discapacidad",
        choices=[
            ("", "Selecciona una categoría"),
            ("Física", "Física"),
            ("Sensorial", "Sensorial"),
            ("Cognitiva", "Cognitiva"),
            ("Psicosocial", "Psicosocial"),
            ("Múltiple", "Múltiple"),
            ("Otra", "Otra")
        ],
        validators=[DataRequired()]
    )

    descripcion = TextAreaField(
        "Descripción de la discapacidad",
        validators=[
            DataRequired(),
            Length(max=250)
        ]
    )

    ruta_certificado = FileField(
        "Certificado de discapacidad",
        validators=[
            Optional(),
            FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                       'Solo se permiten archivos: PDF, JPG, PNG, DOC, DOCX')
        ]
    )


class discapacidadesForm(FlaskForm):

    Info_discapacidades = FieldList(
        FormField(discapacidadItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")