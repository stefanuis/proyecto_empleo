from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)


class ContactoForm(FlaskForm):
    nombres = StringField(
        "Nombre del contacto",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    apellidos = StringField(
        "Apellidos del contacto",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    parentesco = StringField(
        "parentesco con el contacto",
        validators=[
            DataRequired(),
            Length(max=20)
        ]
    )

    tel = StringField(
        "Numero telefono del contacto",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )

    num_resindencia = StringField(
        "Numero fijo, si tiene",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )


    submit = SubmitField("Guardar")
