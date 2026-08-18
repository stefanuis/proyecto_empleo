from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class discapacidadForm(FlaskForm):
    """Formulario para registro de discapacidades"""

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

    submit = SubmitField("Guardar discapacidad")