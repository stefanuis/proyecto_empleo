from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    SubmitField,
    BooleanField
    
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)


class CursoForm(FlaskForm):

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


    certificado = BooleanField(
        "tienen certificacion",
        validators=[DataRequired()]
    )

    fecha_realizacion = DateField(
        "fecha de realizacion de los cursos",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )
