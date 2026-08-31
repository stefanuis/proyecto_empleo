from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required, logout_user
from . import web_bp

@web_bp.route("/")
def login():
    return render_template("login.html")


@web_bp.route("/")
def cerrar():

    logout_user()

    return redirect(url_for("inicio"))