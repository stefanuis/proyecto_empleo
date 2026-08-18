from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    BooleanField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField,

)
from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)

class InforAcademicaItemForm(Form):
    """Formulario para información académica del usuario"""
    registro_id = HiddenField()
    
    tipo = StringField(
        "Tipo de información académica",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    nivel = StringField(
        "Nivel académico",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    estado = StringField(
        "Estado académico",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    periodos_cursados = IntegerField(
        "Períodos cursados académicamente",
        validators=[
            Optional(),
            NumberRange(min=0)
        ]
    )

    area = StringField(
        "Área académica",
        validators=[
            DataRequired(),
            Length(max=30)
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

    pais_institucion = StringField(
        "País de la institución",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    convalidacion = BooleanField(
        "Convalidación",
        validators=[Optional()]
    )

    mes_finalizacion = IntegerField(
        "Mes de finalización",
        validators=[
            Optional(),
            NumberRange(min=1, max=12)
        ]
    )

    anno_finalizacion = IntegerField(
        "Año de finalización",
        validators=[
            Optional(),
            NumberRange(min=1950, max=2030)
        ]
    )

    intensidad_horaria = IntegerField(
        "Intensidad horaria",
        validators=[
            Optional(),
            NumberRange(min=0)
        ]
    )

    ruta_soporte = FileField(
        "Documento de soporte",
        validators=[
            Optional(),
            FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Solo se permiten archivos PDF, Word e imágenes')
        ]
    )



class InforAcademicaForm(FlaskForm):

    Info_academica = FieldList(
        FormField(InforAcademicaItemForm),
        min_entries=1
    )

    submit = SubmitField("Guardar y continuar")

    

