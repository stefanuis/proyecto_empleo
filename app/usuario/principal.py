
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from typing import Optional
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Response

from flask_login import current_user, login_required
import os
from werkzeug.utils import secure_filename
from flask import current_app
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
from app.models.funcion_experiencia import  FuncionExperiencia
from app.models.cursos import Cursos
from app.forms.cursos import CursoForm
from app.forms.competencias import CompetenciasForm
from app.models.competencias import  Competencias 
from app.forms.referencias import referenciasForm
from app.models.referencias import Referencias
from app.models.referencias_personales import ReferenciasPersonales
from app.forms.referencias_personales import referenciasPersonalesForm
from app.forms.discapacidades import discapacidadForm
from app.models.discapacidades import Discapacidades
from app.forms.docs import documentoForm
from app.models.docs import OtrosDocumentos
from app.forms.vacante import VacanteForm
from app.models.vacante import Vacante
from app.models.postulacion import Postulacion
from app.models.citacion import Citaciones
from app.utils.perfil import calcular_completitud_perfil
from app.forms.validaciones import fila_vacia, validar_personal
from app.forms.validaciones import fila_vacia, validar_contacto
from app.forms.validaciones import fila_vacia, validar_familiar
from app.forms.validaciones import fila_vacia, validar_academica
from app.forms.validaciones import fila_vacia ,validar_experiencia
from app.forms.validaciones import fila_vacia,validar_cursos
from app.forms.validaciones import fila_vacia, validar_competencias
from app.forms.validaciones import fila_vacia, validar_referencias
from app.forms.validaciones import fila_vacia, validar_referencias_personales
from app.forms.validaciones import fila_vacia, validar_discapacidades
from .constantes import PASOS_seguimiento, NOMBRES_PASO, DESCRIPCIONES_PASO, TOTAL_PASOS
from app.utils.perfil import calcular_completitud_perfil



from . import usuario_bp



@usuario_bp.context_processor
def inject_progreso():
    endpoint = request.endpoint.split('.')[-1]
    if endpoint in PASOS_seguimiento:
        idx = PASOS_seguimiento.index(endpoint)
        return dict(
            nombre_paso=NOMBRES_PASO[endpoint],
            descripcion_paso=DESCRIPCIONES_PASO[endpoint],
            paso_actual=idx + 1,
            total_pasos=TOTAL_PASOS,
            paso_anterior=PASOS_seguimiento[idx - 1] if idx > 0 else None,
            paso_siguiente=PASOS_seguimiento[idx + 1] if idx < TOTAL_PASOS - 1 else None,
            pasos_rutas=PASOS_seguimiento,
            nombres_cortos_pasos=NOMBRES_PASO,
        )
    return {}


def redirigir_paso_wizard(paso_actual):
    destino = request.form.get("ir_a_paso")
    if destino and destino in PASOS_seguimiento:
        return redirect(url_for(f"usuario.{destino}"))

    idx = PASOS_seguimiento.index(paso_actual)
    siguiente = PASOS_seguimiento[idx + 1] if idx < TOTAL_PASOS - 1 else None
    if siguiente:
        return redirect(url_for(f"usuario.{siguiente}"))

    return redirect(url_for("usuario.resumen"))



@usuario_bp.route("/")
@login_required
def principal():
    # --- KPIs ---
    total_postulaciones = Postulacion.query.filter_by(
        estado="Activa",
        id_usuario=current_user.id
    ).count()

    total_vacantes = Vacante.query.filter_by(
        estado="Activa"
    ).count()

    # --- Fecha de hoy en español ---
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

    # --- Completitud del perfil ---
    completitud = calcular_completitud_perfil(current_user.id)

        # --- Vacantes sugeridas (hero) ---

    areas_candidato = db.session.query(
        Info_academica.area
    ).filter(
        Info_academica.id_usuario == current_user.id,
        Info_academica.area.isnot(None)
    ).distinct().all()

    areas_candidato = [a[0] for a in areas_candidato]

    if areas_candidato:
        vacantes = Vacante.query.filter(
            Vacante.estado == 'Activa',
            Vacante.area_aplicacion.in_(areas_candidato)
        ).order_by(
            Vacante.fecha_publicacion.desc()
        ).limit(3).all()
        sugerencias_personalizadas = True
    else:
        vacantes = Vacante.query.filter(
            Vacante.estado == 'Activa'
        ).order_by(
            Vacante.fecha_publicacion.desc()
        ).limit(3).all()
        sugerencias_personalizadas = False

    return render_template(
        "usuario/principal.html",
        total_postulaciones=total_postulaciones,
        total_vacantes=total_vacantes,
        fecha_hoy=fecha_hoy,
        completitud=completitud,
        vacantes=vacantes,
        sugerencias_personalizadas=sugerencias_personalizadas
    )

##----configuracion
@usuario_bp.route("/beneficios", methods=["GET", "POST"])
@login_required
def beneficios():
    return render_template("usuario/beneficios.html")

@usuario_bp.route("/configuracion", methods=['GET', 'POST'])
@login_required
def configuracion():
    return render_template("usuario/configuracion.html")

@usuario_bp.route("/personal", methods=["GET", "POST"])
@login_required
def personal():

    PASO_ACTUAL = "personal"
    form = InfoPersonalForm()

    registro = Personal.query.filter_by(
        id_usuario=current_user.id
    ).first()

    if request.method == "POST":

        if form.validate():

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

            return redirigir_paso_wizard(PASO_ACTUAL)

        else:
            print("ERRORES:", form.errors)

    elif registro:
        # Solo precargamos en GET (evita pisar lo que el usuario acaba de escribir si hubo error)
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

    return render_template("usuario/personal.html", form=form)

@usuario_bp.route('/contacto', methods=['GET', 'POST'])
@login_required
def contacto():

    PASO_ACTUAL = "contacto"
    form = ContactoForm()

    registro = Contacto.query.filter_by(
        id_usuario=current_user.id
    ).first()

    #validar un formulario , si no existía, lo crea vacío 
    if form.validate_on_submit():
      if not registro:
        registro = Contacto(id_usuario=current_user.id)
        db.session.add(registro)
        registro.fecha_registro = datetime.now()

      registro.nombre = form.nombres.data
      registro.apellido = form.apellidos.data
      registro.parentesco = form.parentesco.data
      registro.tel = form.tel.data
      registro.num_residencia = form.num_residencia.data
      db.session.commit()

      return redirigir_paso_wizard(PASO_ACTUAL)
    
    
      # Precargar 
    if registro:
        form.nombres.data = registro.nombre
        form.apellidos.data = registro.apellido
        form.parentesco.data = registro.parentesco
        form.tel.data = registro.tel
        form.num_residencia.data = registro.num_residencia

    return render_template("usuario/contacto.html",  form=form)


@usuario_bp.route('/familiar', methods=['GET', 'POST'])
@login_required
def familiar():

    PASO_ACTUAL = "familiar"
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
        registro.fecha_realizacion = datetime.now()

        db.session.commit()

        return redirigir_paso_wizard(PASO_ACTUAL)


    # Precargar datos existentes
    if registro:
        form.personas_casa.data = registro.personas_casa
        form.dependen_eco.data = registro.dependen_eco

    return render_template("usuario/familiar.html",form=form)


@usuario_bp.route('/academica', methods=['GET', 'POST'])
@login_required
def academica():

    PASO_ACTUAL = "academica"
    form = InforAcademicaForm()

    if request.method == "GET":
        registros = Info_academica.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_academica.append_entry({
                "registro_id": registro.id,
                "nivel": registro.nivel,
                "estado": registro.estado,
                "periodos_cursados": registro.periodos_cursados,
                "area": registro.area,
                "titulo": registro.titulo,
                "institucion": registro.institucion,
                "pais_institucion": registro.pais_institucion,
                "convalidacion": registro.convalidacion,
                "mes_finalizacion": registro.mes_finalizacion,
                "anno_finalizacion": registro.anno_finalizacion,
                "ruta_soporte": registro.ruta_soporte,
                "intensidad_horaria": registro.intensidad_horaria,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = ["nivel", "estado", "titulo", "institucion", "mes_finalizacion", "anno_finalizacion"]
        errores_negocio = []

        for entry in form.Info_academica:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_academica(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_academica:
                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:
                    registro = Info_academica.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:
                    if registro:
                        db.session.delete(registro)
                    continue

                if fila_vacia(entry, campos):
                    if registro:
                        db.session.delete(registro)
                    continue

                if registro:
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
                    nuevo = Info_academica(
                        id_usuario=current_user.id,
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
           
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template("usuario/academica.html", form=form)

@usuario_bp.route('/experiencia', methods=['GET', 'POST'])
@login_required
def experiencia():

    PASO_ACTUAL = "experiencia"
    form = experienciaForm()

    if request.method == "GET":
        registros = Experiencia.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            funciones_texto = "|".join(f.funcion for f in registro.funciones)

            form.Info_experiencia.append_entry({
                "registro_id": registro.id,
                "entidad": registro.entidad,
                "area": registro.area,
                "cargo": registro.cargo,
                "actual": registro.actual,
                "motivo": registro.motivo,
                "fecha_ingreso": registro.fecha_ingreso,
                "fecha_salida": registro.fecha_salida,
                "pais": registro.pais,
                "departamento": registro.departamento,
                "municipio": registro.municipio,
                "funciones_lista": funciones_texto,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = ["entidad", "area", "cargo", "motivo", "fecha_ingreso", "fecha_salida"]  # ajusta a los campos obligatorios reales
        errores_negocio = []

        for entry in form.Info_experiencia:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_experiencia(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_experiencia:

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:
                    registro = Experiencia.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:
                    if registro:
                        db.session.delete(registro)
                    continue

                if fila_vacia(entry, campos):
                    if registro:
                        db.session.delete(registro)
                    continue

                if registro:
                    # --- Actualizar registro existente ---
                    registro.entidad = entry.entidad.data
                    registro.area = entry.area.data
                    registro.cargo = entry.cargo.data
                    registro.actual = entry.actual.data     
                    registro.motivo = entry.motivo.data if not entry.actual.data else None 
                    registro.fecha_ingreso = entry.fecha_ingreso.data
                    registro.fecha_salida = entry.fecha_salida.data if not entry.actual.data else None
                    registro.pais = entry.pais.data
                    registro.departamento = entry.departamento.data
                    registro.municipio = entry.municipio.data

                else:
                    # --- Crear registro nuevo ---
                    registro = Experiencia(
                        id_usuario=current_user.id,
                        entidad=entry.entidad.data,
                        area=entry.area.data,
                        cargo=entry.cargo.data,
                        actual=entry.actual.data, 
                        motivo=entry.motivo.data if not entry.actual.data else None,   
                        fecha_ingreso=entry.fecha_ingreso.data,
                        fecha_salida=entry.fecha_salida.data if not entry.actual.data else None,
                        pais=entry.pais.data,
                        departamento=entry.departamento.data,
                        municipio=entry.municipio.data,
                    )
                    db.session.add(registro)
                    db.session.flush()  # necesario para obtener registro.id antes de crear sus funciones


                FuncionExperiencia.query.filter_by(id_experiencia=registro.id).delete()

                funciones_texto = entry.funciones_lista.data or ""
                for funcion in funciones_texto.split("|"):
                    funcion = funcion.strip()
                    if funcion:
                        db.session.add(FuncionExperiencia(
                            id_experiencia=registro.id,
                            funcion=funcion
                        ))


            db.session.commit()

            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/experiencia.html",
        form=form
    )


@usuario_bp.route('/cursos', methods=['GET', 'POST'])
@login_required
def cursos():

    PASO_ACTUAL = "cursos"
    form = CursoForm()

    if request.method == "GET":
        registros = Cursos.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_curso.append_entry({
                "registro_id": registro.id,
                "nombre": registro.nombre,
                "institucion": registro.institucion,
                "area": registro.area,
                "horas": registro.horas,
                "fecha_realizacion": registro.fecha_realizacion,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = ["nombre", "institucion", "area", "horas", "fecha_realizacion"]
        errores_negocio = []

        for entry in form.Info_curso:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_cursos(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_curso:

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:

                    registro = Cursos.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:

                    if registro:

                        db.session.delete(registro)

                    continue

                if fila_vacia(entry, campos):

                    if registro:

                        db.session.delete(registro)

                    continue

                if registro:
                    # Editar existente
                    registro.nombre = entry.nombre.data
                    registro.institucion = entry.institucion.data
                    registro.area = entry.area.data
                    registro.horas = entry.horas.data
                    registro.fecha_realizacion = entry.fecha_realizacion.data

                else:
                    # Crear nuevo
                    nuevo = Cursos(
                        id_usuario=current_user.id,
                        nombre=entry.nombre.data,
                        institucion=entry.institucion.data,
                        area=entry.area.data,
                        horas=entry.horas.data,
                        fecha_realizacion=entry.fecha_realizacion.data,
                        certificado=False,
                    )

                    db.session.add(nuevo)

            db.session.commit()

            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/cursos.html", form=form)

@usuario_bp.route('/competencias', methods=['GET', 'POST'])
@login_required
def competencias():

    PASO_ACTUAL = "competencias"
    form = CompetenciasForm()

    if request.method == "GET":
        registros = Competencias.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_competencias.append_entry({
                "registro_id": registro.id,
                "competencia": registro.competencia,
                "nivel": registro.nivel,
                "experiencia": registro.experiencia,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = ["competencia", "nivel"]
        errores_negocio = []

        for entry in form.Info_competencias:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_competencias(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_competencias:

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:

                    registro = Competencias.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:

                    if registro:

                        db.session.delete(registro)

                    continue

                if fila_vacia(entry, campos):

                    if registro:

                        db.session.delete(registro)

                    continue

                if registro:
                    registro.competencia = entry.competencia.data
                    registro.nivel = entry.nivel.data
                    registro.experiencia = entry.experiencia.data
                    registro.fecha_actualizacion = datetime.now()

                else:
                    nuevo = Competencias(
                        id_usuario=current_user.id,
                        competencia=entry.competencia.data,
                        nivel=entry.nivel.data,
                        experiencia=entry.experiencia.data,
                        fecha_actualizacion=datetime.now(),
                    )

                    db.session.add(nuevo)

            db.session.commit()
            flash("Guardado con éxito.", "success")
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/competencias.html", form=form)


@usuario_bp.route('/referencias', methods=['GET', 'POST'])
@login_required
def referencias():

    PASO_ACTUAL = "referencias"
    form = referenciasForm()

    if request.method == "GET":
        registros = Referencias.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_referencias.append_entry({
                "registro_id": registro.id,
                "nombres": registro.nombres,
                "apellidos": registro.apellidos,
                "empresa": registro.empresa,
                "telefono": registro.telefono,
                "ciudad": registro.ciudad,
                "autoriza": registro.autoriza,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = [
            "nombres",
            "apellidos",
            "empresa",
            "telefono",
            "ciudad",
            "autoriza"
        ]

        errores_negocio = []

        for entry in form.Info_referencias:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_referencias(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_referencias:

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:

                    registro = Referencias.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:

                    if registro:

                        db.session.delete(registro)

                    continue

                if fila_vacia(entry, campos):

                    if registro:

                        db.session.delete(registro)

                    continue

                if registro:
                    registro.nombres = entry.nombres.data
                    registro.apellidos = entry.apellidos.data
                    registro.empresa = entry.empresa.data
                    registro.telefono = entry.telefono.data
                    registro.ciudad = entry.ciudad.data
                    registro.autoriza = entry.autoriza.data

                else:
                    nuevo = Referencias(
                        id_usuario=current_user.id,
                        nombres=entry.nombres.data,
                        apellidos=entry.apellidos.data,
                        empresa=entry.empresa.data,
                        telefono=entry.telefono.data,
                        ciudad=entry.ciudad.data,
                        autoriza=entry.autoriza.data,
                        fecha_registro=datetime.now()
                    )

                    db.session.add(nuevo)

            db.session.commit()
            flash("Guardado con éxito.", "success")
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/referencias.html",
        form=form
    )




@usuario_bp.route('/referencias_personales', methods=['GET', 'POST'])
@login_required
def referencias_personales():

    PASO_ACTUAL = "referencias_personales"
    form = referenciasPersonalesForm()

    if request.method == "GET":
        registros = ReferenciasPersonales.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_referencias_personales.append_entry({
                "registro_id": registro.id,
                "nombres": registro.nombres,
                "apellidos": registro.apellidos,
                "parentesco": registro.parentesco,
                "telefono": registro.telefono,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = [
            "nombres",
            "apellidos",
            "parentesco",
            "telefono"
        ]

        errores_negocio = []

        for entry in form.Info_referencias_personales:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_referencias_personales(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for entry in form.Info_referencias_personales:

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:

                    registro = ReferenciasPersonales.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:

                    if registro:

                        db.session.delete(registro)

                    continue

                if fila_vacia(entry, campos):

                    if registro:

                        db.session.delete(registro)

                    continue

                if registro:
                    registro.nombres = entry.nombres.data
                    registro.apellidos = entry.apellidos.data
                    registro.parentesco = entry.parentesco.data
                    registro.telefono = entry.telefono.data

                else:
                    nuevo = ReferenciasPersonales(
                        id_usuario=current_user.id,
                        nombres=entry.nombres.data,
                        apellidos=entry.apellidos.data,
                        parentesco=entry.parentesco.data,
                        telefono=entry.telefono.data,
                    )

                    db.session.add(nuevo)

            db.session.commit()
            flash("Guardado con éxito.", "success")
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/referencias_personales.html",
        form=form
    )

@usuario_bp.route('/discapacidades', methods=['GET', 'POST'])
@login_required
def discapacidades():

    PASO_ACTUAL = "discapacidades"
    form = discapacidadForm()

    if request.method == "GET":
        registros = Discapacidades.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_discapacidades.append_entry({
                "registro_id": registro.id,
                "categoria": registro.categoria,
                "descripcion": registro.descripcion,
                "tiene_certificado": registro.tiene_certificado,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = [
            "categoria",
            "descripcion",
            "tiene_certificado"
        ]

        errores_negocio = []

        for entry in form.Info_discapacidades:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_discapacidades(entry)
            errores_negocio.extend(errores_fila)

        if errores_negocio:

            for error in errores_negocio:
                flash(error, "danger")

        else:

            for i, entry in enumerate(form.Info_discapacidades):

                registro_id = entry.registro_id.data
                marcado_para_eliminar = entry.eliminar.data == "1"
                registro = None

                if registro_id:
                    registro = Discapacidades.query.filter_by(
                        id=registro_id,
                        id_usuario=current_user.id
                    ).first()

                if marcado_para_eliminar:

                    if registro:
                        db.session.delete(registro)

                    continue

                if fila_vacia(entry, campos):

                    if registro:
                        db.session.delete(registro)

                    continue

                if registro:
                    registro.categoria = entry.categoria.data
                    registro.descripcion = entry.descripcion.data
                    registro.tiene_certificado = entry.tiene_certificado.data

                else:
                    registro = Discapacidades(
                        id_usuario=current_user.id,
                        categoria=entry.categoria.data,
                        descripcion=entry.descripcion.data,
                        tiene_certificado=entry.tiene_certificado.data,
                        fecha_registro=datetime.now(),
                    )

                    db.session.add(registro)
                    db.session.flush()

                nombre_campo_archivo = (
                    f"Info_discapacidades-{i}-ruta_certificado"
                )

                archivo = request.files.get(nombre_campo_archivo)

                if archivo and archivo.filename:
                    nombre_seguro = secure_filename(archivo.filename)

                    nombre_final = (
                        f"discapacidad_{registro.id}_{nombre_seguro}"
                    )

                    ruta_carpeta = os.path.join(
                        "app",
                        "static",
                        "uploads",
                        "discapacidades"
                    )

                    os.makedirs(ruta_carpeta, exist_ok=True)

                    ruta_archivo = os.path.join(
                        ruta_carpeta,
                        nombre_final
                    )

                    archivo.save(ruta_archivo)

                    registro.ruta_certificado = (
                        f"uploads/discapacidades/{nombre_final}"
                    )

                if not entry.tiene_certificado.data:
                    registro.ruta_certificado = None

            db.session.commit()
            flash("Guardado con éxito.", "success")
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/discapacidades.html",
        form=form
    )




@usuario_bp.route('/documentos', methods=['GET', 'POST'])
@login_required
def documentos() -> str | Response:
    form: documentoForm = documentoForm()

    if form.validate_on_submit():
        for entry_form in form.Info_docs:
            archivo: Optional[FileStorage] = entry_form.ruta_soporte.data

            # Si esta fila no trae archivo (quedó vacía), se ignora
            if not archivo or archivo.filename == "":
                continue

            nombre_original: str = secure_filename(archivo.filename)
            nombre_unico: str = (
                f"{current_user.id}_"
                f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_"
                f"{nombre_original}"
            )

            carpeta_destino: str = os.path.join(
                current_app.root_path, "static", "uploads", "docs"
            )
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_completa: str = os.path.join(carpeta_destino, nombre_unico)

            try:
                archivo.save(ruta_completa)
            except OSError:
                flash(f"No se pudo guardar el archivo {nombre_original}.", "danger")
                continue

            ruta_relativa: str = f"uploads/docs/{nombre_unico}"

            nuevo_doc = OtrosDocumentos(
                id_usuario=current_user.id,
                nombre=entry_form.nombre.data,
                tipo=entry_form.tipo.data,
                ruta_soporte=ruta_relativa,
                fecha_registro=datetime.now()
            )
            db.session.add(nuevo_doc)

        db.session.commit()
        flash("Documentos guardados exitosamente.", "success")
        return redirect(url_for("usuario.registro_completo"))

    docs: list[OtrosDocumentos] = OtrosDocumentos.query.filter_by(
        id_usuario=current_user.id
    ).order_by(OtrosDocumentos.fecha_registro.desc()).all()

    return render_template("usuario/docs.html", form=form )


@usuario_bp.route("/documentos/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_documento(id: int) -> Response:
    documento: Optional[OtrosDocumentos] = OtrosDocumentos.query.filter_by(
        id=id,
        id_usuario=current_user.id
    ).first()

    if documento:
        ruta_absoluta: str = os.path.join(
            current_app.root_path, "static", documento.ruta_soporte
        )
        if os.path.exists(ruta_absoluta):
            os.remove(ruta_absoluta)

        db.session.delete(documento)
        db.session.commit()
        flash("Documento eliminado correctamente.", "success")
    else:
        flash("No se encontró el documento o no tienes permiso para eliminarlo.", "danger")

    return redirect(url_for("usuario.documentos"))



@usuario_bp.route("/registro-completo")
@login_required
def registro_completo():
    return render_template("usuario/registro_completo.html")


### vacantes consultas sql filtros 

@usuario_bp.route('/vacantes/<int:id>', methods=["GET"])
@login_required
def detalle_vacante(id):
    vac = Vacante.query.get_or_404(id)
    return render_template("detalle_vacante.html", vacante=vac)

@usuario_bp.route('/vacantes', methods=["GET"])
@login_required
def vacantes():
    accion = request.args.get("accion", "")
    q = request.args.get("q", "").strip()
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    nivel = request.args.get("nivel", "").strip()
    estado = request.args.get("estado", "Activa")

    query = Vacante.query.filter_by(estado=estado)

    if accion == "buscar":
        if q:
            query = query.filter(Vacante.titulo.ilike(f"%{q}%"))

    elif accion == "filtrar":
        if area_aplicacion:
            query = query.filter(Vacante.area_aplicacion == area_aplicacion)

        if nivel:
            query = query.filter(Vacante.nivel_academico == nivel)

    vacantes = query.order_by(Vacante.fecha_publicacion.desc()).all()

    areas_aplicacion = (
        VacanteForm
        .area_aplicacion
        .kwargs["choices"]
    )

    return render_template(
        "usuario/vacantes.html",
        vacantes=vacantes,
        areas=areas_aplicacion,
        q=q,
        area_aplicacion_seleccionada=area_aplicacion,
        nivel_seleccionado=nivel
    )
@usuario_bp.route("/vacantes/<int:id>/postular", methods=["POST"])
@login_required
def postular(id):
    vac = Vacante.query.get_or_404(id)

    if vac.estado != "Activa":
        flash("Esta vacante ya no está disponible.", "danger")
        return redirect(url_for("usuario.vacantes"))

    completitud = calcular_completitud_perfil(current_user.id)

    if completitud["porcentaje"] < 100:
        flash(
            "Debes completar tu perfil antes de postularte. Te falta: "
            + ", ".join(completitud["faltantes"]) + ".",
            "warning"
        )
        return redirect(url_for(f"usuario.{completitud['primer_paso_faltante']}"))

    ya_postulado = Postulacion.query.filter_by(
        id_usuario=current_user.id,
        id_vacante=id
    ).first()

    if ya_postulado:
        flash("Ya te has postulado a esta vacante.", "warning")
        return redirect(url_for("usuario.vacantes"))

    nueva_postulacion = Postulacion(
        id_usuario=current_user.id,
        id_vacante=id,
        estado="postulado"
    )

    db.session.add(nueva_postulacion)
    db.session.commit()

    flash("¡Te has postulado correctamente!", "success")
    return redirect(url_for("usuario.mis_postulaciones"))

##------ mis postulaciones----------

@usuario_bp.route('/mis-postulaciones', methods=['GET'])
@login_required
def mis_postulaciones():
    q = request.args.get('q', '').strip()
    estado_filtro = request.args.get('estado', '')

    query = db.session.query(Postulacion, Vacante).join(
        Vacante, Vacante.id == Postulacion.id_vacante
    ).filter(
        Postulacion.id_usuario == current_user.id
    )

    if q:
        query = query.filter(Vacante.titulo.ilike(f'%{q}%'))
    if estado_filtro:
        query = query.filter(Postulacion.estado == estado_filtro)

    resultados = query.order_by(Postulacion.fecha_postulacion.desc()).all()

    # Mapeo de estado -> número de paso para el stepper
    PASOS = {'postulado': 1, 'revision': 2, 'entrevista': 3}

    postulaciones = []
    for post, vacante in resultados:
        if post.estado in ('contratado', 'rechazado'):
            paso_actual = 4
        else:
            paso_actual = PASOS.get(post.estado, 1)

        postulaciones.append({
            'post': post,
            'vacante': vacante,
            'paso_actual': paso_actual
        })

    return render_template(
        'usuario/postulaciones.html',
        postulaciones=postulaciones
    )

@usuario_bp.route('/postulaciones/<int:id>/retirar', methods=['POST'])
@login_required
def retirar_postulacion(id):
    postulacion = Postulacion.query.filter(
        Postulacion.id == id,
        Postulacion.id_usuario == current_user.id
    ).first_or_404()

    if postulacion.estado == 'retirada':
        flash('Esta postulación ya estaba retirada.', 'warning')
        return redirect(url_for('usuario.mis_postulaciones'))

    if postulacion.estado in ('contratado', 'rechazado'):
        flash('No puedes retirar una postulación que ya fue finalizada.', 'warning')
        return redirect(url_for('usuario.mis_postulaciones'))

    postulacion.estado = 'retirada'
    db.session.commit()

    flash('Has retirado tu postulación. No podrás volver a postularte a esta vacante.', 'success')
    return redirect(url_for('usuario.mis_postulaciones'))


####### gestion de envios de correo 

@usuario_bp.route('/citacion/responder/<token>/<respuesta>')
def responder_citacion(token, respuesta):
    citacion = Citaciones.query.filter_by(token=token).first_or_404()

    if respuesta not in ['confirmar', 'rechazar']:
        flash('Enlace inválido.', 'error')
        return render_template('usuario/respuesta_citacion.html', citacion=None)

    # Si ya respondió antes, no permitir sobreescribir
    if citacion.respuesta:
        return render_template(
            'usuario/respuesta_citacion.html',
            citacion=citacion,
            ya_respondida=True
        )

    citacion.respuesta = 'confirmada' if respuesta == 'confirmar' else 'rechazada'
    citacion.estado = 'confirmada' if respuesta == 'confirmar' else 'rechazada'
    citacion.fecha_respuesta = datetime.now()
    db.session.commit()

    return render_template(
        'usuario/respuesta_citacion.html',
        citacion=citacion,
        respuesta=respuesta
    )