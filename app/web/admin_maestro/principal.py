from flask import render_template, flash

from app.models.user import User

from . import admin_maestro_bp

from app.forms.administradores import CrearAdministradorForm

import secrets

from app.extensions import db

from app.utils.permisos import exigir_rol

from app.web.registro import enviar_invitacion_admin


@admin_maestro_bp.before_request
def verificar_admin_maestro():
    return exigir_rol("admin_maestro")


@admin_maestro_bp.route("/")
def inicial():

    return render_template(
        "admin_maestro/principal.html"
    )


@admin_maestro_bp.route("/crear-administrador", methods=["GET", "POST"])
def crear_administrador():

    form = CrearAdministradorForm()

    if form.validate_on_submit():

        # El login compara el correo en minúsculas
        correo = form.correo.data.strip().lower()
        usuario_existente = User.query.filter_by(correo=correo).first()

        if usuario_existente:
            # Administrador que nunca activó su cuenta: se le reenvía el enlace
            if usuario_existente.rol == "admin" and not usuario_existente.esta_verificada:
                enviado = enviar_invitacion_admin(usuario_existente)
                db.session.commit()
                if enviado:
                    flash("Ese administrador aún no había activado su cuenta: se le reenvió el enlace.", "success")
                else:
                    flash("No se pudo reenviar el correo de activación. Intenta de nuevo.", "danger")
            else:
                flash("Ya existe un usuario creado con este correo.", "danger")

            return render_template("admin_maestro/crear_usuarios.html", form=form)

        nuevo_admin = User(
            nombres=form.nombres.data,
            apellidos=form.apellidos.data,
            correo=correo,
            telefono=form.telefono.data,
            rol="admin",
        )
        # Contraseña aleatoria que nadie conoce: el administrador define la
        # suya con el enlace que le llega por correo
        nuevo_admin.set_password(secrets.token_urlsafe(32))

        db.session.add(nuevo_admin)
        enviado = enviar_invitacion_admin(nuevo_admin)
        db.session.commit()

        if enviado:
            flash(
                f"Administrador registrado. Se envió a {correo} el enlace para crear su contraseña.",
                "success"
            )
        else:
            flash(
                "El administrador quedó registrado, pero no se pudo enviar el correo. "
                "Vuelve a crearlo con el mismo correo para reenviar el enlace.",
                "warning"
            )

    return render_template(
        "admin_maestro/crear_usuarios.html",
        form=form
    )
