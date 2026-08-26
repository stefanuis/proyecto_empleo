from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    IntegerField,
    SelectField,
    DateField,
    TextAreaField,
    BooleanField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange,
    Length
)

class competenciasItemForm(Form):
    """Formulario para registro de competencias profesionales"""

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

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


class CompetenciasForm(FlaskForm):
    Info_competencias = FieldList(
        FormField(competenciasItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")