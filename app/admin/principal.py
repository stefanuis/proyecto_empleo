
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.user import User

from . import admin_bp


@admin_bp.route("/", methods=["GET"])
@login_required
def inicial():
    print("Hola mundo")
    return "Hola mundo desde el bp admin"
    #return render_template("Hola mundo desde el bp usuario")




