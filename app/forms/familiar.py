from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    NumberRange
)


class familiarForm(FlaskForm):
    """Formulario para información familiar"""

    personas_casa = IntegerField(
        "Número de personas en la casa",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=20)
        ]
    )

    dependen_eco = IntegerField(
        "Número de dependientes económicos",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=20)
        ]
    )

    submit = SubmitField("Guardar información familiar")
