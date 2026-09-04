from flask import render_template, flash

from app.models.user import User

from . import admin_maestro_bp

from app.forms.administradores import CrearAdministradorForm

import secrets

from werkzeug.security import generate_password_hash

from datetime import datetime

from app.extensions import db, mail


@admin_maestro_bp.route("/")
def inicial():

    return render_template(
        "admin_maestro/principal.html"
    )


@admin_maestro_bp.route("/crear-administrador", methods=["GET", "POST"])
def crear_administrador():

    form = CrearAdministradorForm()


    if form.validate_on_submit():

        usuario_existente = User.query.filter_by(
            correo = form.correo.data

        ).first()

        if usuario_existente:
            flash("Ya existe un usuario creado con este correo.", "danger")

            return render_template("admin_maestro//crear_usuarios.html", form=form)
        
        mi_token = secrets.token_urlsafe(32)

        clave_temporal = secrets.token_urlsafe(32)

        clave_hash = generate_password_hash(clave_temporal)


        nuevo_admin = User(

            nombres=form.nombres.data,

            apellidos=form.apellidos.data,

            correo=form.correo.data,

            telefono=form.telefono.data,

            clave_hash=clave_hash,

            rol="admin",

            token=mi_token,

            token_envio=datetime.now()
        )


        db.session.add(nuevo_admin)

        db.session.commit()


        flash("El administrador ha sido registrado correctamente.","success")


    return render_template(
        "admin_maestro/crear_usuarios.html",
        form=form
    )

