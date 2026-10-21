from flask import (
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required
from . import web_bp
from app.utils.sesion import cerrar_sesion


@web_bp.route("/cerrar-sesion")
def cerrar():

    cerrar_sesion()

    # El script de inactividad llega aquí con ?motivo=inactividad
    if request.args.get("motivo") == "inactividad":
        flash("Tu sesión se cerró por inactividad. Vuelve a iniciar sesión.", "warning")
    else:
        flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("web.login"))


@web_bp.route("/sesion/mantener")
@login_required
def mantener_sesion():
    # El before_request ya renovó la actividad; aquí no hay nada más que hacer
    return "", 204
