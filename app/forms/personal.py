from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    Length,
    NumberRange
)


class InfoPersonalForm(FlaskForm):

    nombres = StringField(
        "Nombres",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    apellidos = StringField(
        "Apellidos",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    tipo_doc = SelectField(
        "Tipo de documento",
        choices=[
            ("", "Seleccione"),
            ("CC", "Cédula de ciudadanía"),
            ("TI", "Tarjeta de identidad"),
            ("CE", "Cédula de extranjería"),
            ("PP", "Pasaporte"),
            ("PEP", "Permiso Especial de Permanencia"),
            ("PPT", "Permiso por Protección Temporal"),
            ("OTRO", "Otro")
        ],
        validators=[DataRequired()]
    )

    num_doc = StringField(
        "Número de documento",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    fecha_exp_doc = DateField(
        "Fecha de expedición",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    fecha_nacimiento = DateField(
        "Fecha de nacimiento",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    genero = SelectField(
        "Género",
        choices=[
            ("", "Seleccione"),
            ("Masculino", "Masculino"),
            ("Femenino", "Femenino"),
            ("Otro", "Otro"),
            ("Prefiero no responder", "Prefiero no responder")
        ],
        validators=[Optional()]
    )

    email = StringField(
        "Correo electrónico",
        validators=[
            Optional(),
            Email(),
            Length(max=150)
        ]
    )

    num_cel = StringField(
        "Celular principal",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )

    num_cel_dos = StringField(
        "Celular secundario",
        validators=[
            Optional(),
            Length(max=20)
        ]
    )

    grupo_etnico = SelectField(
        "Grupo étnico",
        choices=[
            ("", "Seleccione"),
            ("Ninguno", "Ninguno"),
            ("Indígena", "Indígena"),
            ("Afrocolombiano", "Afrocolombiano"),
            ("Otro", "Otro")
        ],
        validators=[Optional()]
    )


    departamento = StringField(
        "Departamento de Nacimiento",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    municipio = StringField(
        "Municipio de Nacimiento",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    barrio = StringField(
        "Barrio o vereda donde vive",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    direccion = StringField(
        "Dirección donde vive",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    nacionalidad = StringField(
        "Nacionalidad",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    vive_rural = SelectField(
        "¿Vive en zona rural?",
        choices=[
            ("", "Seleccione"),
            ("SI", "Sí"),
            ("NO", "No")
        ],
        validators=[Optional()]
    )

    estado_civil = SelectField(
        "Estado civil",
        choices=[
            ("", "Seleccione"),
            ("Soltero", "Soltero"),
            ("Casado", "Casado"),
            ("Unión Libre", "Unión Libre"),
            ("Separado", "Separado"),
            ("Divorciado", "Divorciado"),
            ("Viudo", "Viudo")
        ],
        validators=[Optional()]
    )

    personas_cargo = IntegerField(
        "Personas a cargo",
        validators=[
            Optional(),
            NumberRange(min=0)
        ]
    )

    submit = SubmitField("Guardar")



    