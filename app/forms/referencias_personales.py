from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import (
    StringField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Length
)


class referenciaPersonalItemForm(Form):
    """Formulario para registro de referencias personales"""

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

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
        "Parentesco/Relación",
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(),
            Length(max=20)
        ]
    )


class referenciasPersonalesForm(FlaskForm):

    Info_referencias_personales = FieldList(
        FormField(referenciaPersonalItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")