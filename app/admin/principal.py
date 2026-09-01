
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from sqlalchemy import exists
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.vacante import Vacante
from app.forms.vacante import VacanteForm
from app.models.postulacion import Postulacion
from app.models.personal import Personal
from app.models.contacto import Contacto
from app.models.academica import Info_academica
from app.models.familiar import Familiar
from app.models.referencias import Referencias
from app.forms.postulacion import PostulacionForm


from . import admin_bp


@admin_bp.route("/principal", methods=["GET"])
@login_required
def inicial():
    if(session["rol"] == "admin"):
        vacantes_labels = ['Analista de Datos', 'Coord. Logística', 'Contador Junior', 'Ejecutivo Comercial']
        vacantes_data = [22, 18, 15, 9]
        hoy = datetime.now()

        dias = [
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]

        meses = [
            "enero", "febrero", "marzo", "abril",
            "mayo", "junio", "julio", "agosto",
            "septiembre", "octubre", "noviembre", "diciembre"
        ]

        fecha_hoy = f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]}"

        return render_template(
            'admin/principal.html',
            vacantes_labels=vacantes_labels,
            vacantes_data=vacantes_data,
            total_vacantes_activas=18,
            total_hojas=241,
            total_entrevistas=12,
            total_por_cerrar=4,
            fecha_hoy=fecha_hoy
        )
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")

@admin_bp.route("/vacantes")
@login_required
def listar_vacantes():
    if(session["rol"] == "admin"):
        q = request.args.get('q', '').strip()
        area = request.args.get('area', '')
        estado = request.args.get('estado', '')

        query = Vacante.query

        if q:
            query = query.filter(Vacante.titulo.ilike(f'%{q}%'))
        if area:
            query = query.filter_by(area=area)
        if estado:
            query = query.filter_by(estado=estado)

        vacantes = query.order_by(Vacante.fecha_publicacion.desc()).all()


        return render_template("admin/listar_vacante.html", vacantes=vacantes)
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route("/vacantes/crear", methods=["GET", "POST"])
@login_required
def crear_vacante():
    if(session["rol"] == "admin"):
        form = VacanteForm()

        if form.validate_on_submit():
            nueva_vacante = Vacante(
                titulo=form.titulo.data,
                area=form.area.data,
                descripcion=form.descripcion.data,
                requisito=form.requisito.data,
                salario=form.salario.data,
                estado=form.estado.data,
                fecha_publicacion=form.fecha_publicacion.data,
                fecha_cierre=form.fecha_cierre.data,    
                id_usuario_creador=current_user.id
            )
            db.session.add(nueva_vacante)
            db.session.commit()

            flash("Vacante creada correctamente.", "success")
            return redirect(url_for("admin.listar_vacantes"))

        return render_template("admin/crear_vacantes.html", form=form)
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route("/vacantes/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_vacante(id):
    if(session["rol"] == "admin"):
        vacante = Vacante.query.get_or_404(id)
        form = VacanteForm(obj=vacante)

        if form.validate_on_submit():
            form.populate_obj(vacante)   # copia los datos del form al objeto
            db.session.commit()
            flash("Vacante actualizada correctamente.", "success")
            return redirect(url_for("admin.listar_vacantes"))

        return render_template("admin/crear_vacantes.html", form=form)  # reutiliza el mismo template
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")


@admin_bp.route("/vacantes/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_vacante(id):
    if(session["rol"] == "admin"):
        vacante =  Vacante.query.get_or_404(id)
        db.session.delete(vacante)
        db.session.commit()
        flash("Vacante eliminada.", "success")
        return redirect(url_for("admin.listar_vacantes"))
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")


@admin_bp.route("/vacantes/<int:id>/postulantes", methods=["GET"])
@login_required
def listar_postulantes(id):
    if(session["rol"] == "admin"):
        vacante = Vacante.query.get_or_404(id)
        estado = request.args.get('estado', '')

        query = db.session.query(
            Postulacion,
            Personal
        ).join(
            Personal,
            Personal.id_usuario == Postulacion.id_usuario
        ).filter(
            Postulacion.id_vacante == id
        )

        if estado:
            query = query.filter(Postulacion.estado == estado)

        postulaciones = query.order_by(Postulacion.fecha_postulacion.desc()).all()

        return render_template(
            "admin/postulantes_vacantes.html",
            vacante=vacante,
            postulaciones=postulaciones
        )
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route('/hojas-de-vida')
def listar_hojas():
    if(session["rol"] == "admin"):
        return render_template('admin/listar_hojas.html')
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route('/postulante/<int:id>/expediente')
def ver_expediente(id):
    if(session["rol"] == "admin"):
        post = Postulacion.query.get_or_404(id)
        vacante = Vacante.query.get_or_404(post.id_vacante)

        personal = Personal.query.filter_by(id_usuario=post.id_usuario).first()
        contacto = Contacto.query.filter_by(id_usuario=post.id_usuario).first()
        academica = Info_academica.query.filter_by(id_usuario=post.id_usuario).all()
        familiar = Familiar.query.filter_by(id_usuario=post.id_usuario).first()
        referencias = Referencias.query.filter_by(id_usuario=post.id_usuario).all()

        return render_template('admin/expediente.html',
                                post=post,
                                vacante=vacante,
                                personal=personal,
                                contacto=contacto,
                                academica=academica,
                                familiar=familiar,
                                referencias=referencias)
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route("/postulacion/<int:id>/actualizar", methods=["POST"])
@login_required
def actualizar_postulacion(id):
    if(session["rol"] == "admin"):
        postulacion = Postulacion.query.get_or_404(id)

        postulacion.estado = request.form["estado"]
        postulacion.notas_reclutador = request.form["notas_reclutador"]
        postulacion.fecha_actualizacion = datetime.now()

        db.session.commit()

        return redirect(url_for('admin.listar_postulantes', id=postulacion.id_vacante))
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")
    

@admin_bp.route("/postulaciones")
@login_required
def listar_postulaciones():
    if(session["rol"] == "admin"):
        q = request.args.get('q', '').strip()
        nivel = request.args.get('nivel', '')
        area = request.args.get('area', '')
        estado = request.args.get('estado', '')

        query = db.session.query(
            Postulacion, Personal, Vacante
        ).join(
            Personal, Personal.id_usuario == Postulacion.id_usuario
        ).join(
            Vacante, Vacante.id == Postulacion.id_vacante
        )

        if q:
            query = query.filter(
                db.or_(
                    Personal.nombres.ilike(f'%{q}%'),
                    Personal.apellidos.ilike(f'%{q}%')
                )
            )

        if nivel:
            query = query.filter(
                exists().where(   # <-- acá se usa exists
                    (Info_academica.id_usuario == Postulacion.id_usuario) &
                    (Info_academica.nivel == nivel)
                )
            )

        if area:
            query = query.filter(Vacante.area == area)

        if estado:
            query = query.filter(Postulacion.estado == estado)

        resultados = query.order_by(Postulacion.fecha_postulacion.desc()).all()

        return render_template(
            "admin/listar_postulantes.html",
            resultados=resultados
        )
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")



