from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, SubmitField

from wtforms.validators import DataRequired, Email, Length


class CrearAdministradorForm(FlaskForm):

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


    correo = EmailField(
        "Correo electrónico",
        validators=[
            DataRequired(),
            Email(),
            Length(max=150)
        ]
    )


    telefono = StringField(
        "Teléfono",
        validators=[
            Length(max=20)
        ]
    )


    submit = SubmitField(
        "Crear administrador"
    )