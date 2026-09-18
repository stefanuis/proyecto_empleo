from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length



class CitacionForm(FlaskForm):

    fecha = DateField(
        "Fecha de la entrevista",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    hora = TimeField(
        "Hora",
        format="%H:%M",
        validators=[DataRequired()]
    )

    lugar = StringField(
        "Lugar o enlace",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    mensaje = TextAreaField(
        "Mensaje adicional",
        validators=[
            Optional()
        ]
    )

    submit = SubmitField(
        "Enviar citación"
    )