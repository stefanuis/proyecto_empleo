from flask import render_template, request, url_for, redirect, flash
from app.forms.registro import RegistroForm
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from app.models.user import User
from app.extensions import db, mail

from . import web_bp

TOKEN_EXPIRACION_MINUTOS = 30

def enviar_correo(email, el_token, nombres):
    enlace = url_for(
        'web.confirmacion',
        token=el_token,
        _external=True
    )

    try:
        msg = Message(
            subject='Enlace de verificacion - Clinica Panamericana',
            sender='noresponder@clinpanamericana.com',
            recipients=[email]
        )
        msg.attach(
            filename="logo_color.png",
            content_type="image/png",
            data=open("app/static/img/logo_color.png", "rb").read(),
            disposition="inline",
            headers={"Content-ID": "<logo_color>"}
        )
        msg.html = render_template("mensaje.html", nombres=nombres,enlace=enlace, minutos=TOKEN_EXPIRACION_MINUTOS)
        mail.send(msg)
    except Exception as e:
        print(f'Error al enviar el correo. Intenta nuevamente más tarde.', 'error')
        print("ERROR SMTP:")
        print(type(e))
        print(str(e))


@web_bp.route("/registro", methods=["GET"])
def registro():
    form=RegistroForm()
    return render_template("registro.html", form=form)


@web_bp.route('/registro', methods=['POST'])
def registro_post():
    form = RegistroForm()
    if form.validate_on_submit():
        # Todo está correcto, procesa los datos
        
        d_registro = {}
        d_registro["nombres"] = request.form.get("nombres")
        d_registro["apellidos"] = request.form.get("apellidos")
        d_registro["email"] = request.form.get("email")
        d_registro["telefono"] = request.form.get("telefono")
        d_registro["password"] = request.form.get("password")
        d_registro["confirm_password"] = request.form.get("confirm_password")
        d_registro["terms"] = request.form.get("terms")

        #print(d_registro)

        usuario = User.query.filter_by(
            correo=form.email.data
        ).first()

        if usuario:

            if(usuario.esta_verificada == 1):
                flash(
                    "Ya existe una cuenta registrada con ese correo.",
                    "danger"
                )
                return render_template('registro.html', form=form)

            else:
                envio = usuario.token_envio 
                diferencia = datetime.now() - envio
                minutos = diferencia.total_seconds() / 60
                minutos = round(minutos, 1) 

                if(minutos > TOKEN_EXPIRACION_MINUTOS):
                    mi_token = secrets.token_urlsafe(32)
                    usuario.token = mi_token
                    usuario.token_envio = datetime.now()
                    db.session.commit()
                    enviar_correo(email=usuario.correo, el_token=mi_token, nombres=usuario.nombres)
                    return render_template("c_registro.html", email=usuario.correo)

                else:
                    pendiente = 30 - minutos
                    pendiente = round(pendiente, 1)
                    flash(
                        f"Esta cuenta tiene aun pendiente una verificacion de correo activa por {pendiente} minutos.",
                        "warning"
                    )
                    return render_template('registro.html', form=form)

        else:
            mi_token = secrets.token_urlsafe(32)
            nuevo_usuario = User(
                nombres=form.nombres.data,
                apellidos=form.apellidos.data,
                correo=form.email.data,
                telefono=form.telefono.data,
                token = mi_token,
                token_envio = datetime.now()
            )

            nuevo_usuario.set_password(
                form.password.data
            )

            db.session.add(nuevo_usuario)
            db.session.commit()

            enviar_correo(email=form.email.data, el_token=mi_token, nombres=form.nombres.data)
        
        return render_template("c_registro.html", email=form.email.data)
        #return redirect(url_for('exito'))
    
    
    # Si es GET o hay errores, muestra el template
    return render_template('registro.html', form=form)


@web_bp.route("/confirmacion/<token>", methods=["GET"])
def confirmacion(token):
    """
    Verifica la cuenta del usuario a partir del token enviado por correo.
    """

    # Buscar el usuario asociado al token
    usuario = User.query.filter_by(token=token).first()

    if usuario is None:
        flash(
            "El enlace de verificación no es válido o ya fue utilizado.",
            "danger"
        )
        return redirect(url_for("web.login"))

    # Verificar que exista la fecha de generación del token
    if usuario.token_envio is None:
        flash(
            "El enlace de verificación no es válido.",
            "danger"
        )
        return redirect(url_for("web.login"))

    # Si ya fue verificada anteriormente
    if usuario.esta_verificada:
        flash(
            "Esta cuenta ya se encuentra verificada. Puede iniciar sesión.",
            "info"
        )
        return redirect(url_for("web.login"))

    # Verificar expiración del token
    tiempo_transcurrido = datetime.now() - usuario.token_envio

    if tiempo_transcurrido > timedelta(minutes=TOKEN_EXPIRACION_MINUTOS):

        # Invalidar el token vencido
        usuario.token = None
        usuario.token_envio = None
        db.session.commit()

        flash(
            "El enlace de verificación ha expirado. Solicite uno nuevo.",
            "warning"
        )
        return redirect(url_for("web.login"))

    # Activar la cuenta
    usuario.esta_verificada = True
    usuario.esta_activa = True

    # Invalidar el token para que no pueda reutilizarse
    usuario.token = None
    usuario.token_envio = None

    db.session.commit()

    flash(
        "¡Su cuenta ha sido verificada correctamente! Ya puede iniciar sesión.",
        "success"
    )

    return redirect(url_for("web.login"))