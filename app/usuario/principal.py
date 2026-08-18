
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
from app.forms.personal import InfoPersonalForm
from app.forms.contacto import ContactoForm
from app.models.contacto import Contacto
from app.forms.familiar import familiarForm
from app.models.familiar import Familiar
from app.forms.academica import InforAcademicaForm
from app.models.academica import Info_academica
from app.forms.experiencia import experienciaForm
from app.models.experiencia import Experiencia
from app.forms.cursos import cursoForm
from app.models.cursos import Cursos
from app.forms.competencias import competenciasForm
from app.models.competencias import  Competencias 
from app.forms.referencias import referenciasForm
from app.models.referencias import Referencias
from app.forms.discapacidades import discapacidadForm
from app.models.discapacidades import Discapacidades
from app.forms.docs import documentoForm
from app.models.docs import Docs


from . import usuario_bp


#eso me ayudara a saber por donde voy


PASOS_seguimiento = [
    "personal",
    "contacto",
    "familiar",
    "academica",
    "experiencia",
    "cursos",
    "competencias",
    "referencias",
    "discapacidades",
    "documentos",
]

TOTAL_PASOS = len(PASOS_seguimiento)

NOMBRES_PASO = {
    "personal": "Información Personal",
    "contacto": "Información de Contacto",
    "familiar": "Información Familiar",
    "academica": "Formación Académica",
    "experiencia": "Experiencia Laboral",
    "cursos": "Cursos y Certificaciones",
    "competencias": "Competencias",
    "referencias": "Referencias Laborales",
    "discapacidades": "Discapacidades",
    "documentos": "Documentos Soportantes",
}

# 3. El context_processor - va aquí, después de las constantes, 
#    y ANTES o DESPUÉS de tus rutas (el orden respecto a las rutas no importa)
@usuario_bp.context_processor
def inject_progreso():
    endpoint = request.endpoint.split('.')[-1]
    if endpoint in PASOS_seguimiento:
        idx = PASOS_seguimiento.index(endpoint)
        return dict(
            nombre_paso=NOMBRES_PASO[endpoint],
            paso_actual=idx + 1,
            total_pasos=TOTAL_PASOS,
            paso_anterior=PASOS_seguimiento[idx - 1] if idx > 0 else None
        )
    return {}




@usuario_bp.route("/", methods=["GET"])
@login_required
def inicial():
    misDatos = {
        "anio": 2026,
        "version": "0.01",
        "titulo": "Principal mi Usuario"
    }
    return render_template("principal.html", datos=misDatos)



@usuario_bp.route("/personal", methods=["GET", "POST"])
@login_required
def personal():
    form = InfoPersonalForm()

    registro = Personal.query.filter_by(
        id_usuario=current_user.id
    ).first()

    if form.validate_on_submit():
        if not registro:
            registro = Personal(id_usuario=current_user.id)
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

        db.session.commit()


        return redirect(url_for("usuario.contacto"))

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


    return render_template("usuario/personal.html", form=form,  paso_actual=1, total_pasos=10)

@usuario_bp.route('/contacto', methods=['GET', 'POST'])
@login_required
def contacto():

    form = ContactoForm()

    registro = Contacto.query.filter_by(
        id_usuario=current_user.id
    ).first()

    #validar un formulario , si no existía, lo crea vacío 
    if form.validate_on_submit():
        if not registro:
            registro = Contacto(id_usuario=current_user.id)

            #este objeto es nuevo, agrégalo para que se guarde
            db.session.add(registro)

            registro.nombre =  form.nombres.data
            registro.apellido = form.apellidos.data
            registro.parentesco = form.parentesco.data
            registro.tel = form.tel.data
            registro.num_residencia =  form.num_residencia.data
            registro.fecha_registro = datetime.now()
            db.session.commit()

            
        return redirect(url_for("usuario.familiar"))
            #sirve para saber en que posicion esta 

        #precargar lo existente para mostrarlo
    if registro:

            form.nombres.data = registro.nombre
            form.apellidos.data = registro.apellido
            form.parentesco.data = registro.parentesco
            form.tel.data = registro.tel
            form.num_residencia.data = registro.num_residencia

    return render_template("usuario/contacto.html",  form=form,  paso_actual=2, total_pasos=10)

@usuario_bp.route('/familiar', methods=['GET', 'POST'])
@login_required
def familiar():

    form = familiarForm()

    registro = Familiar.query.filter_by(
        id_usuario=current_user.id
    ).first()

    if form.validate_on_submit():


        if not registro:
            registro = Familiar(
                id_usuario=current_user.id
            )

            db.session.add(registro)


        registro.personas_casa = form.personas_casa.data
        registro.dependen_eco = form.dependen_eco.data

        db.session.commit()


        return redirect(url_for("usuario.academica"))

    # Precargar datos existentes
    if registro:
        form.personas_casa.data = registro.personas_casa
        form.dependen_eco.data = registro.dependen_eco

    return render_template("usuario/familiar.html",form=form, paso_actual=3, total_pasos=10)

@usuario_bp.route('/academica', methods=['GET', 'POST'])
@login_required
def academica():
    form = InforAcademicaForm()


    if request.method == "GET":
        registros = Info_academica.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_academica.append_entry({
            "registro_id": registro.id,
            "entidad": registro.entidad,
            "area": registro.area,
            "cargo": registro.cargo,
            "actual": registro.actual,
            "motivo": registro.motivo,
            "otro": registro.otro,
            "fecha_ingreso": registro.fecha_ingreso,
            "fecha_salida": registro.fecha_salida,
            "pais": registro.pais,
            "departamento": registro.departamento,
            "municipio": registro.municipio,
            "funciones_realizadas": registro.funciones_realizadas,
            }) 
    if form.validate_on_submit():
        for entry in form.Info_academica:
            registro_id = entry.registro_id.data
            
            registro = None
            if registro_id:
                registro = Info_academica.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

            if registro:
                # editar existente
                registro.tipo = entry.tipo.data  #el valor que el usuario escribió (o que trae precargado) en el campo tipo de este subformulario
                registro.nivel = entry.nivel.data
                registro.estado = entry.estado.data
                registro.periodos_cursados = entry.periodos_cursados.data
                registro.area = entry.area.data
                registro.titulo = entry.titulo.data
                registro.institucion = entry.institucion.data
                registro.pais_institucion = entry.pais_institucion.data
                registro.convalidacion = entry.convalidacion.data
                registro.mes_finalizacion = entry.mes_finalizacion.data
                registro.anno_finalizacion = entry.anno_finalizacion.data
                registro.intensidad_horaria = entry.intensidad_horaria.data
            else:
                # crear nuevo
  
                nuevo = Info_academica(
                    id_usuario=current_user.id,
                    tipo=entry.tipo.data,
                    nivel=entry.nivel.data,
                    estado=entry.estado.data,
                    periodos_cursados=entry.periodos_cursados.data,
                    area=entry.area.data,
                    titulo=entry.titulo.data,
                    institucion=entry.institucion.data,
                    pais_institucion=entry.pais_institucion.data,
                    convalidacion=entry.convalidacion.data,
                    mes_finalizacion=entry.mes_finalizacion.data,
                    anno_finalizacion=entry.anno_finalizacion.data,
                    intensidad_horaria=entry.intensidad_horaria.data,
                )
                db.session.add(nuevo)

        db.session.commit()

        return redirect(url_for("usuario.experiencia"))

    return render_template("usuario/academica.html", form=form)


@usuario_bp.route('/experiencia', methods=['GET', 'POST'])
@login_required
def experiencia():
    form =  experienciaForm()

    if request.method == "GET":
        registro = Experiencia.query.filter_by(
            id_usuario = current_user.id
        ).all()


        for registros in registro:
            form.EX
            
@usuario_bp.route('/cursos', methods=['GET', 'POST'])
@login_required
def cursos():


@usuario_bp.route('/competencias', methods=['GET', 'POST'])
def competencias():
    pass

@usuario_bp.route('/referencias', methods=['GET', 'POST'])
def referencias():
    pass

@usuario_bp.route('/discapacidades', methods=['GET', 'POST'])
def discapacidades():
    pass

@usuario_bp.route('/documentos', methods=['GET', 'POST'])
def documentos():
    pass

    #"Si el formulario fue enviado y además todos los campos pasan las validaciones
    #valida si los campos son validos