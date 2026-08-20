from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class referenciasItemForm(Form):
    """Formulario para registro de referencias profesionales"""

    nombres = StringField(
        "Nombres",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    apellidos = StringField(
        "Apellidos",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    parentesco = StringField(
        "Parentesco/Relación laboral",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    empresa = StringField(
        "Empresa/Institución",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )

    autoriza = SelectField(
        "¿Autoriza contacto?",
        choices=[
            ("", "Selecciona"),
            ("Si", "Sí"),
            ("No", "No")
        ],
        validators=[DataRequired()]
    )
class referenciasForm(FlaskForm):

    Info_referencias = FieldList(
    FormField(referenciasItemForm),
        min_entries=0
    )

submit = SubmitField("Guardar y continuar")