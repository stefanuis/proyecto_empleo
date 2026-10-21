from flask import render_template
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from flask_login import login_user, current_user
from datetime import datetime
import time
from app.extensions import db
from app.models.user import User
from app.utils.permisos import url_panel

from . import web_bp


@web_bp.route("/", methods=["GET"])
def login():
    # Con sesión abierta (p. ej. al usar "Atrás") no se muestra el login
    if current_user.is_authenticated:
        return redirect(url_panel(current_user.rol))

    return render_template("login.html")



@web_bp.route("/", methods=["POST"])
def login_post():
    correo = request.form.get("correo", "").strip().lower()
    clave = request.form.get("clave", "").strip()

    if not correo or not clave:
        flash("Debe ingresar correo y contraseña.", "warning")
        return render_template("login.html")

    usuario = User.query.filter_by(correo=correo).first()

    if usuario is None or not usuario.check_password(clave):
        flash("Credenciales incorrectas.", "danger")
        return render_template("login.html")


    if not usuario.esta_activa:
        flash("La cuenta está desactivada.", "warning")
        return render_template("login.html")


    if not usuario.esta_verificada:
        flash("Debe verificar su correo.", "warning")
        return render_template("login.html")


    usuario.ultimo_login = datetime.now()
    db.session.commit()

    # Sesión nueva: se descarta cualquier dato de una sesión anterior
    session.clear()
    login_user(usuario)

    session["rol"] = usuario.rol
    session["ultima_actividad"] = time.time()

    return redirect(url_panel(usuario.rol))



