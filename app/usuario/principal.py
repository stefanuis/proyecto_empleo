
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
from app.models.personal import Personal
from app.models.contacto import Contacto
from app.forms.personal import InfoPersonalForm
from app.forms.contacto import ContactoForm
from app.forms.cursos import CursoForm

from . import usuario_bp

@usuario_bp.route("/", methods=["GET"])
@login_required
def inicial():
    misDatos = {
        "anio": 2026,
        "version": "0.01",
        "titulo": "Principal mi Usuario"
    }
    return render_template("principal.html", datos=misDatos)



@usuario_bp.route("/personal", methods=["GET"])
@login_required
def personal():
    form = InfoPersonalForm()

    registro = Personal.query.filter_by(
        id_usuario=current_user.id
    ).first()

    if registro:

        form.nombres.data = registro.nombres
        form.apellidos.data = registro.apellidos
        form.tipo_doc.data = registro.tipo_doc
        form.num_doc.data = registro.num_doc
        form.fecha_exp_doc.data = registro.fecha_exp_doc
        form.fecha_nacimiento.data = registro.fecha_nacimiento
        form.genero.data = registro.genero
        form.email.data = registro.email
        form.num_cel.data = registro.num_cel
        form.num_cel_dos.data = registro.num_cel_dos
        form.grupo_etnico.data = registro.grupo_etnico
        form.departamento.data = registro.departamento
        form.municipio.data = registro.municipio
        form.barrio.data = registro.barrio
        form.direccion.data = registro.direccion
        form.nacionalidad.data = registro.nacionalidad
        form.vive_rural.data = registro.vive_rural
        form.estado_civil.data = registro.estado_civil
        form.personas_cargo.data = registro.personas_cargo

    misDatos = {
        "anio": 2026,
        "version": "0.01",
        "titulo": "Informacion Personal"
    }
    return render_template("personal.html", datos=misDatos, form=form)


@usuario_bp.route("/personal", methods=["POST"])
@login_required
def personal_post():

    form = InfoPersonalForm()

    registro = Personal.query.filter_by(
        id_usuario=current_user.id
    ).first()

    #print(request.method)
    #print(form.validate())
    #print(form.errors)

    if form.validate_on_submit():

        if registro is None:
            registro = Personal(
                id_usuario=current_user.id
            )
            db.session.add(registro)

        registro.nombres = form.nombres.data
        registro.apellidos = form.apellidos.data
        registro.tipo_doc = form.tipo_doc.data
        registro.num_doc = form.num_doc.data
        registro.fecha_exp_doc = form.fecha_exp_doc.data
        registro.fecha_nacimiento = form.fecha_nacimiento.data
        registro.genero = form.genero.data
        registro.email = form.email.data
        registro.num_cel = form.num_cel.data
        registro.num_cel_dos = form.num_cel_dos.data
        registro.grupo_etnico = form.grupo_etnico.data
        registro.departamento = form.departamento.data
        registro.municipio = form.municipio.data
        registro.barrio = form.barrio.data
        registro.direccion = form.direccion.data
        registro.nacionalidad = form.nacionalidad.data
        registro.vive_rural = form.vive_rural.data
        registro.estado_civil = form.estado_civil.data
        registro.personas_cargo = form.personas_cargo.data
        registro.ultima_actualizacion = datetime.now()

        db.session.commit()

        flash(
            "La información personal fue guardada correctamente.",
            "success"
        )

        return redirect(
            url_for("usuario.personal")
        )


    flash(
        "Debe suministrar todos los campos del formulario",
        "warning"
    )

    return redirect(
        url_for("usuario.personal")
    )



@usuario_bp.route("/contacto", methods=["GET"])
@login_required
def contacto():
    form = ContactoForm()

    registro = Contacto(
        id_usuario=current_user.id
    ).first()

    if registro:
        form.nombres.data = registro.nombre
        form.apellidos.data = registro.apellido
        form.parentesco.data = registro.parentesco
        form.tel.data = registro.tel
        form.num_resindencia.data = registro.num_residencia
        

    misDatos = {
        "anio": 2026,
        "version": "0.01",
        "titulo": "Informacion de Contacto"
    }
    return render_template("contacto.html", datos=misDatos, form=form)

@usuario_bp.route("/curso", methods=["GET"])
@login_required
def cursos():
    form =  CursoForm()

    registro = cursos(
        id_usuario=current_user.id
    ).first()

    if registro:
        form.nombre.data =  registro.nombre
        form.institucion = registro.institucion
        form.area = registro.area
        form.horas =  registro.horas
        form.certificado =  registro.certificado
        form.fecha_realizacion =  registro.fecha_realizacion

        return redirect(url_for("lista_cursos"))

    return render_template(
        "curso/nuevo.html",form=form
    )

@usuario_bp.route("/discapacidades", methods=["GET"])
@login_required
def discapacidades():

    formm = 

    registro = discapacidades(
        id_usuario=current_user.id
    ).first()

    if registro:
        


    #"Si el formulario fue enviado y además todos los campos pasan las validaciones
      #valida si los campos son validos
    
  