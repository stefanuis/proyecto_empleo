from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
    TextAreaField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class PostulacionForm(FlaskForm):
    """Formulario para registro de postulaciones a vacantes"""

    id_vacante = HiddenField(
        "ID Vacante",
        validators=[DataRequired()]
    )

    estado = SelectField(
        "Estado de la postulación",
        choices=[
            ("", "Selecciona un estado"),
            ("Pendiente", "Pendiente"),
            ("En revisión", "En revisión"),
            ("Aceptado", "Aceptado"),
            ("Rechazado", "Rechazado"),
            ("Retirada", "Retirada")
        ],
        validators=[Optional()]
    )

    notas_reclutador = TextAreaField(
        "Notas del reclutador",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    submit = SubmitField("Enviar postulación")
