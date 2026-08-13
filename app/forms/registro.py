from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegistroForm(FlaskForm):
    # Nombres
    nombres = StringField(
        "Nombres",
        validators=[
            DataRequired(message="Debe ingresar su nombre."),
            Length(min=2, max=80, message="El nombre debe tener entre 2 y 80 caracteres."),
            Regexp('^[A-Za-záéíóúñÁÉÍÓÚÑ\\s]+$', 
                message="El nombre solo puede contener letras y espacios."),
                DataRequired("Debe ingresar sus nombres")
        ]
    )

    # Apellido
    apellidos = StringField(
        "Apellidos",
        validators=[
            DataRequired(message="Debe ingresar sus apellidos."),
            Length(min=2, max=80, message="Los apellidos debe tener entre 2 y 80 caracteres."),
            Regexp('^[A-Za-záéíóúñÁÉÍÓÚÑ\\s]+$', 
                message="Los apellidos solo puede contener letras y espacios."),
                DataRequired("Debe ingresar sus apellidos")
        ]
    )
    
    # Correo electrónico
    email = EmailField(
        "Correo electrónico",
        validators=[
            DataRequired(message="Debe ingresar un correo electrónico."),
            Email(message="Debe ingresar un correo electrónico válido."),
            Length(max=120, message="El correo no puede superar los 120 caracteres."),
            DataRequired("Debe ingresar un correo electrónico válido")
        ]
    )
    
    telefono = StringField(
        "Número de teléfono",
        validators=[
            DataRequired(message="Debe ingresar un número de teléfono."),
            Length(min=7, max=15, message="El teléfono debe tener entre 7 y 15 dígitos."),
            Regexp('^[0-9\\+\\-\\(\\)\\s]+$', 
                message="Ingrese un número de teléfono válido (solo dígitos, +, -, espacios y paréntesis)."),
                DataRequired("Debe suministrar un número de teléfono")
        ]
    )

    # Contraseña
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="Debe ingresar una contraseña."),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres."),
            Regexp(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)',
                message="La contraseña debe contener al menos una mayúscula, una minúscula y un número."
            ),
            DataRequired("Debe ingresar una contraseña")
        ]
    )
    
    # Confirmar contraseña
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Debe confirmar la contraseña."),
            EqualTo('password', message="Las contraseñas no coinciden."),
            DataRequired("Debe confirmar la contraseña")
        ]
    )

    terms = BooleanField(
        "Acepto términos y condiciones",
        validators=[DataRequired(message="Debes aceptar términos y condiciones.")]
    )
    
    # Botón de envío
    submit = SubmitField("Registrarse")