from flask_wtf import FlaskForm
from wtforms import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    FieldList,
    FormField
)
from wtforms.validators import (
    DataRequired,
    Length
)


class documentoItemForm(Form):
    """Formulario para un documento individual"""

    nombre = StringField(
        "Nombre del documento",
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )

    ruta_soporte = FileField(
        "Cargar documento",
        validators=[
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


class documentoForm(FlaskForm):
    """Formulario contenedor para subir varios documentos a la vez"""

    Info_docs = FieldList(
        FormField(documentoItemForm),
        min_entries=1
    )

    submit = SubmitField("Guardar documento")