from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    DateField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length
)


class documentoForm(FlaskForm):
    """Formulario para registro de documentos"""

    nombre = StringField(
        "Nombre del documento",
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )


    ruta = FileField(
            "Cargar documento",
            validators=[
                DataRequired(),
                FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 
                        'Solo se permiten archivos: PDF, JPG, PNG, DOC, DOCX')
            ]
        )

    tipo = SelectField(
        "Tipo de documento",
        choices=[
            ("", "Selecciona un tipo"),
            ("Cédula", "Cédula"),
            ("Diploma", "Diploma"),
            ("Certificado", "Certificado"),
            ("Licencia", "Licencia"),
            ("Recomendación", "Recomendación"),
            ("Constancia", "Constancia"),
            ("Otro", "Otro")
        ],
        validators=[DataRequired()]
    )


    submit = SubmitField("Guardar documento")
