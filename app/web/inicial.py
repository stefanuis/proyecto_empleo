from flask import render_template
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from flask_login import login_user
from datetime import datetime
from app.extensions import db
from app.models.user import User

from . import web_bp


@web_bp.route("/", methods=["GET"])
def login_get():

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

    login_user(usuario)



    if(usuario.rol == "admin"):
        print("Este es admin")
        return redirect(url_for("admin.inicial"))
    else:
        print("Este no es admin")
        return redirect(url_for("usuario.inicial"))




