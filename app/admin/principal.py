
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
from app.forms.vacante import VacanteForm
from app.forms.postulacion import PostulacionForm

from . import admin_bp


@admin_bp.route("/", methods=["GET"])
@login_required
def inicial():

    return render_template("admin/principal.html")
    #return render_template("Hola mundo desde el bp usuario")


@admin_bp.route('/vacante', methods=['GET', 'POST'])
@login_required
def crear_vacantes():

    form = VacanteForm()
    if form.validate_on_submit():

        db.session.add()

        titulo = form.titulo.data
        area = form.area.data
        descripcion = form.area.data
        requisito = form.requisito.data
        salario = form.salario.data
        estado =  form.estado.data
        fecha_publicacion = form.fecha_publicacion.data
        fecha_cierre = form.fecha_cierre.data

        db.session.commit()

    

