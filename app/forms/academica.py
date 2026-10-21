from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import (
    StringField,
    SelectField,
    IntegerField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField,
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange
)

# El área de aplicación del candidato se registra una sola vez en el
# Perfil profesional; aquí solo van los datos esenciales de cada estudio.
class InforAcademicaItemForm(Form):
    """Formulario para información académica del usuario"""
    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    nivel = SelectField(
    "Tipo de formación académica",
    choices=[
        ("Bachillerato", "Bachillerato"),
        ("tecnico", "Técnico"),
        ("tecnologo", "Tecnólogo"),
        ("universitario", "Universitario"),
        ("especializacion", "Especialización"),
        ("maestria", "Maestría"),
        ("doctorado", "Doctorado")
    ],
    validators=[
        DataRequired()
    ]
)

    estado = SelectField(
    "Estado académico",
    choices=[
        ("en_curso", "En curso"),
        ("finalizado", "Finalizado"),
        ("incompleto", "Incompleto"),
        ("aplazado", "Aplazado"),
        ("cancelado", "Cancelado"),
    ],
    validators=[
        DataRequired()
    ]
)

    titulo = StringField(
        "Título obtenido",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    institucion = StringField(
        "Institución educativa",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    mes_finalizacion = IntegerField(
        "Mes de finalización",
        validators=[
            Optional(),
            NumberRange(
                min=1,
                max=12,
                message="El mes debe ser un número entre 1 y 12.",
            )
        ]
    )

    anno_finalizacion = IntegerField(
        "Año de finalización",
        validators=[
            Optional(),
            NumberRange(min=1950)
        ]
    )


class InforAcademicaForm(FlaskForm):

    Info_academica = FieldList(
        FormField(InforAcademicaItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")
