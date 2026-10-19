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
    BooleanField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)
from app.constantes import DISCAPACIDAD_CATEGORIAS


class discapacidadItemForm(Form):

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    categoria = SelectField(
        "Categoría de discapacidad",
        choices=DISCAPACIDAD_CATEGORIAS,
        validators=[DataRequired()]
    )

    descripcion = TextAreaField(
        "Descripción de la discapacidad",
        validators=[
            DataRequired(),
            Length(max=250)
        ]
    )

    tiene_certificado = BooleanField(
        "¿Tiene certificado?"
    )

    ruta_certificado = FileField(
        "Certificado de discapacidad",
        validators=[
            Optional(),
            FileAllowed(
                ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                'Solo se permiten archivos: PDF, JPG, PNG, DOC, DOCX'
            )
        ]
    )


class discapacidadForm(FlaskForm):
    Info_discapacidades = FieldList(
        FormField(discapacidadItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")