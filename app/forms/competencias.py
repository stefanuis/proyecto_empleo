from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange
)


class competenciasForm(FlaskForm):
    """Formulario para registro de competencias profesionales"""

    competencia = StringField(
        "Competencia",
        validators=[
            DataRequired(),
            Length(min=3, max=150)
        ],

    )

    nivel = SelectField(
        "Nivel de dominio",
        choices=[
            ("", "Selecciona un nivel"),
            ("Básico", "Básico"),
            ("Intermedio", "Intermedio"),
            ("Avanzado", "Avanzado"),
            ("Experto", "Experto")
        ],
        validators=[DataRequired()]
    )

    experiencia = IntegerField(
        "Años de experiencia",
        validators=[
            Optional(),
            NumberRange(min=0, max=70)
        ],
        render_kw={"placeholder": "Ej: 5"}
    )

    submit = SubmitField("Guardar competencia")
