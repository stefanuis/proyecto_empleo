from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    TextAreaField,
    DateField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class VacanteForm(FlaskForm):
    """Formulario para registro de vacantes laborales"""

    titulo = StringField(
        "Título del puesto",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    area = StringField(
        "Área/Departamento",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    descripcion = TextAreaField(
        "Descripción de la vacante",
        validators=[
            DataRequired(),
            Length(max=500)
        ]
    )

    requisito = TextAreaField(
        "Requisitos",
        validators=[
            DataRequired(),
            Length(max=500)
        ]
    )

    salario = TextAreaField(
        "Información de salario",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    estado = SelectField(
        "Estado de la vacante",
        choices=[
            ("", "Selecciona un estado"),
            ("Activa", "Activa"),
            ("Cerrada", "Cerrada"),
            ("Suspendida", "Suspendida"),
            ("Cancelada", "Cancelada")
        ],
        validators=[DataRequired()]
    )

    fecha_cierre = DateField(
        "Fecha de cierre",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    submit = SubmitField("Guardar vacante")
