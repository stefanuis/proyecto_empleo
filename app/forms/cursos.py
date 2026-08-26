from wtforms import Form
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    SubmitField,
    BooleanField,
    FieldList,
    FormField,
    HiddenField
    
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)


class cursoItemForm(Form):

    registro_id = HiddenField()
    eliminar = HiddenField(default="0")

    nombre = StringField(
        "nombre del curso",
        validators=[
            DataRequired(),
            Length(max= 100)
        ]
    )

    institucion = StringField(
    "institucion de los cursos",
        validators=[
            DataRequired(),
                Length(max= 100)
        ]
    )

    area = StringField(
        "area del cursos",
        validators=[
            DataRequired(),
            Length(max= 100)
        ]
    )

    horas = IntegerField(
        "horas de los cursos",
        validators=[
            DataRequired()
        ]
    )
    fecha_realizacion = DateField(
        "fecha de realizacion de los cursos",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )
class CursoForm(FlaskForm):

    Info_curso = FieldList(
    FormField(cursoItemForm),
        min_entries=0
    )

    submit = SubmitField("Guardar y continuar")


