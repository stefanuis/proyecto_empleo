
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models import vacante
from app.forms.vacante import VacanteForm
from app.forms.postulacion import PostulacionForm

from . import admin_bp


@admin_bp.route("/", methods=["GET"])
@login_required
def inicial():

    return render_template("admin/principal.html")
    #return render_template("Hola mundo desde el bp usuario")

@admin_bp.route("/vacantes")
@login_required
def listar_vacantes():
    vacantes = vacante.query.order_by(vacante.fecha_publicacion.desc()).all()
    return render_template("admin/listar_vacantes.html", vacantes=vacantes)


@admin_bp.route("/vacantes/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_vacante(id):
    vacante = vacante.query.get_or_404(id)
    form = VacanteForm(obj=vacante)

    if form.validate_on_submit():
        form.populate_obj(vacante)   # copia los datos del form al objeto
        db.session.commit()
        flash("Vacante actualizada correctamente.", "success")
        return redirect(url_for("admin.listar_vacantes"))

    return render_template("admin/crear_vacante.html", form=form)  # reutiliza el mismo template


@admin_bp.route("/vacantes/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_vacante(id):
    vacante =  vacante.query.get_or_404(id)
    db.session.delete(vacante)
    db.session.commit()
    flash("Vacante eliminada.", "success")
    return redirect(url_for("admin.listar_vacantes"))

    

