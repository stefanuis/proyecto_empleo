from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DateField,
    IntegerField,
    SubmitField
)
from datetime import date

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    ValidationError,
)
from app.constantes import GRUPO_ETNICO_OPCIONES
from app.forms.validaciones import EDAD_MAXIMA, EDAD_MINIMA, sumar_anios


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
        validators=[DataRequired(message="La fecha de expedición es obligatoria y debe ser una fecha válida.")]
    )

    fecha_nacimiento = DateField(
        "Fecha de nacimiento",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha de nacimiento es obligatoria y debe ser una fecha válida.")]
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
        choices=GRUPO_ETNICO_OPCIONES,
        validators=[Optional()]
    )


    departamento = SelectField(
        "Departamento de Nacimiento",
        choices=[("", "Seleccione")],
        validators=[Optional()]
    )

    municipio = SelectField(
        "Municipio de Nacimiento",
        choices=[("", "Seleccione")],
        validators=[Optional()]
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

    # WTForms ejecuta automáticamente los métodos validate_<campo>

    def validate_fecha_nacimiento(self, field):
        hoy = date.today()
        if field.data > hoy:
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        if sumar_anios(field.data, EDAD_MINIMA) > hoy:
            raise ValidationError(f"Debes tener al menos {EDAD_MINIMA} años.")
        if sumar_anios(field.data, EDAD_MAXIMA) < hoy:
            raise ValidationError("Revisa la fecha de nacimiento: la edad no es válida.")

    def validate_fecha_exp_doc(self, field):
        if field.data > date.today():
            raise ValidationError("La fecha de expedición no puede ser futura.")

        nacimiento = self.fecha_nacimiento.data
        if not nacimiento:
            return
        if field.data < nacimiento:
            raise ValidationError(
                "La fecha de expedición no puede ser anterior a la de nacimiento."
            )
        # La cédula de ciudadanía solo se expide desde los 18 años
        if self.tipo_doc.data == "CC" and field.data < sumar_anios(nacimiento, 18):
            raise ValidationError(
                "La cédula de ciudadanía se expide a partir de los 18 años; "
                "revisa la fecha de expedición o la de nacimiento."
            )



    