
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)
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
from app.forms.experiencia import experienciaForm
from app.models.cursos import Cursos
from app.forms.cursos import CursoForm
from app.forms.competencias import competenciasForm
from app.models.competencias import  Competencias 
from app.forms.referencias import referenciasForm
from app.models.referencias import Referencias
from app.forms.discapacidades import discapacidadesForm
from app.models.discapacidades import Discapacidades
from app.forms.docs import documentoForm
from app.models.docs import Docs
from app.models import vacante
from app.models.postulacion import postulacion


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
    return render_template("usuario/principal.html",datos=misDatos)



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
            })

    if form.validate_on_submit():

        ids_enviados = []

        for entry in form.Info_academica:

            registro_id = entry.registro_id.data
            registro = None

            if registro_id:
                registro = Info_academica.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

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

                ids_enviados.append(registro.id)

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
                db.session.flush()

                ids_enviados.append(nuevo.id)

        # Eliminar solo los que ya no están en el formulario
        if ids_enviados:
            Info_academica.query.filter(
                Info_academica.id_usuario == current_user.id,
                ~Info_academica.id.in_(ids_enviados)
            ).delete(synchronize_session=False)

        else:
            Info_academica.query.filter_by(
                id_usuario=current_user.id
            ).delete(synchronize_session=False)

        db.session.commit()

        return redirect(url_for("usuario.experiencia"))

    return render_template(
        "usuario/academica.html", form=form,paso_actual=4, total_pasos=10,paso_anterior="contacto"
    )




@usuario_bp.route("/experiencia", methods=["GET", "POST"])
@login_required
def experiencia():

    form = experienciaForm()

    if request.method == "GET":

        registros = Experiencia.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_experiencia.append_entry({
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
                "funciones_realizadas": registro.funciones_realizadas
            })

    if form.validate_on_submit():

        ids_enviados = []

        for entry in form.Info_experiencia:

            registro_id = entry.registro_id.data

            registro = None

            if registro_id:
                registro = Experiencia.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

            if registro:

                registro.entidad = entry.entidad.data
                registro.area = entry.area.data
                registro.cargo = entry.cargo.data
                registro.actual = entry.actual.data
                registro.motivo = entry.motivo.data
                registro.otro = entry.otro.data
                registro.fecha_ingreso = entry.fecha_ingreso.data
                registro.fecha_salida = entry.fecha_salida.data
                registro.pais = entry.pais.data
                registro.departamento = entry.departamento.data
                registro.municipio = entry.municipio.data
                registro.funciones_realizadas = entry.funciones_realizadas.data

                ids_enviados.append(registro.id)

            else:

                nuevo = Experiencia(
                    id_usuario=current_user.id,
                    entidad=entry.entidad.data,
                    area=entry.area.data,
                    cargo=entry.cargo.data,
                    actual=entry.actual.data,
                    motivo=entry.motivo.data,
                    otro=entry.otro.data,
                    fecha_ingreso=entry.fecha_ingreso.data,
                    fecha_salida=entry.fecha_salida.data,
                    pais=entry.pais.data,
                    departamento=entry.departamento.data,
                    municipio=entry.municipio.data,
                    funciones_realizadas=entry.funciones_realizadas.data,
                    fecha_registro=datetime.now()
                )

                db.session.add(nuevo)
                db.session.flush()

                ids_enviados.append(nuevo.id)

        # Eliminar solamente los registros que ya no están en el formulario
    

        db.session.commit()

        return redirect(url_for("usuario.curso"))

    return render_template(
        "usuario/experiencia.html",
        form=form,paso_actual=5, total_pasos=10, paso_anterior="academica"
    )

@usuario_bp.route("/cursos", methods=["GET", "POST"])
@login_required
def curso():

    form = CursoForm()  



    if request.method == "GET":
        registros = Cursos.query.filter_by(
            id_usuario=current_user.id
        ).all()

        if request.method == " POST":
            print("POST recibido")
            print("VALIDA:", form.validate())
            print("ERRORES:", form.errors)

        for registro in registros:
            form.Info_curso.append_entry({
                "registro_id": registro.id,
                "nombre": registro.nombre,
                "institucion": registro.institucion,
                "area": registro.area,
                "horas": registro.horas,
                "fecha_realizacion": registro.fecha_realizacion,
                "certificado": registro.certificado
            })

    if form.validate_on_submit():
        ids_enviados = []

        for entry in form.Info_curso:

            registro_id = entry.registro_id.data
            registro = None

            if registro_id:
                registro = Cursos.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

            if registro:
                # Editar existente
                registro.nombre = entry.nombre.data
                registro.institucion = entry.institucion.data
                registro.area = entry.area.data
                registro.horas = entry.horas.data
                registro.fecha_realizacion = entry.fecha_realizacion.data
                registro.certificado = entry.certificado.data

                ids_enviados.append(registro.id)

            else:
                # Crear nuevo
                nuevo = Cursos(
                    id_usuario=current_user.id,
                    nombre=entry.nombre.data,
                    institucion=entry.institucion.data,
                    area=entry.area.data,
                    horas=entry.horas.data,
                    fecha_realizacion=entry.fecha_realizacion.data,
                    certificado=entry.certificado.data,
                )

                db.session.add(nuevo)
                db.session.flush()

                ids_enviados.append(nuevo.id)


        db.session.commit()

        return redirect(url_for("usuario.referencias"))

    return render_template(
        "usuario/cursos.html",
        form=form,
        paso_actual=5,
        total_pasos=10,
        paso_anterior="experiencia"
    )


@usuario_bp.route('/referencias', methods=['GET', 'POST'])
@login_required
def referencias():

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
                "parentesco": registro.parentesco,
                "empresa": registro.empresa,
                "telefono": registro.telefono,
                "ciudad": registro.ciudad,
                "autoriza": registro.autoriza,
            })

    if form.validate_on_submit():

        ids_enviados = []

        for entry in form.Info_referencias:

            registro_id = entry.registro_id.data

            registro = None

            if registro_id:
                registro = Referencias.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

            if registro:

                # Editar existente
                registro.nombres = entry.nombres.data
                registro.apellidos = entry.apellidos.data
                registro.parentesco = entry.parentesco.data
                registro.empresa = entry.empresa.data
                registro.telefono = entry.telefono.data
                registro.ciudad = entry.ciudad.data
                registro.autoriza = entry.autoriza.data

                ids_enviados.append(registro.id)

            else:

                # Crear nuevo
                nuevo = Referencias(
                    id_usuario=current_user.id,
                    nombres=entry.nombres.data,
                    apellidos=entry.apellidos.data,
                    parentesco=entry.parentesco.data,
                    empresa=entry.empresa.data,
                    telefono=entry.telefono.data,
                    ciudad=entry.ciudad.data,
                    autoriza=entry.autoriza.data,
                    fecha_registro=datetime.utcnow()
                )

                db.session.add(nuevo)
                db.session.flush()

                ids_enviados.append(nuevo.id)

        # Eliminar solamente las referencias que fueron quitadas del formulario
        if ids_enviados:

            Referencias.query.filter(
                Referencias.id_usuario == current_user.id,
                ~Referencias.id.in_(ids_enviados)
            ).delete(synchronize_session=False)

        else:

            # Se eliminaron todas las referencias
            Referencias.query.filter_by(
                id_usuario=current_user.id
            ).delete(synchronize_session=False)

        db.session.commit()

        return redirect(url_for("usuario.discapacidades"))

    return render_template(
        "usuario/referencias.html",
        form=form,
        paso_actual=5,
        total_pasos=10,
        paso_anterior="cursos"
    )
usuario_bp.route('/discapacidades', methods=['GET', 'POST'])
@login_required
def discapacidades():
    form = discapacidadesForm()

    if request.method == "GET":
        registros = Discapacidades.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            form.Info_discapacidades.append_entry({
                "registro_id": registro.id,
                "categoria": registro.categoria,
                "descripcion": registro.descripcion,
            })

    if form.validate_on_submit():
        ids_enviados=[]

        for entry in form.Info_discapacidades:
            registro_id = entry.registro_id.data

            registro = None
            if registro_id:
                registro = Discapacidades.query.filter_by(
                    id=registro_id,
                    id_usuario=current_user.id
                ).first()

            if registro:
                # editar existente
                registro.categoria = entry.categoria.data
                registro.descripcion = entry.descripcion.data
            else:
                # crear nuevo
                nuevo = Discapacidades(
                    id_usuario=current_user.id,
                    categoria=entry.categoria.data,
                    descripcion=entry.descripcion.data,
                    fecha_registro=datetime.now(),
                )
                db.session.add(nuevo)
                db.session.flush()
                ids_enviados.append(nuevo.id)


        db.session.commit()

        return redirect(url_for("usuario.documentos"))

    return render_template("usuario/discapacidades.html", form=form, paso_anterior="referencias")


#-----------#subir los documentos#--------------#
@usuario_bp.route("/documentos", methods=["GET", "POST"])
@login_required
def documentos():
    form = documentoForm()

    if form.validate_on_submit():
        for entry in form.Info_docs:
            archivo = entry.ruta.data

            # Si esta fila no trae archivo (quedó vacía), se ignora
            if not archivo or archivo.filename == "":
                continue

            nombre_original = secure_filename(archivo.filename)
            nombre_unico = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{nombre_original}"

            carpeta_destino = os.path.join(current_app.root_path, "static", "uploads", "docs")
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_completa = os.path.join(carpeta_destino, nombre_unico)
            archivo.save(ruta_completa)

            ruta_relativa = f"uploads/docs/{nombre_unico}"

            nuevo_doc = Docs(
                id_usuario=current_user.id,
                nombre=entry.nombre.data,
                ruta=ruta_relativa,
                tipo=entry.tipo.data,
                fecha_actualizacion=datetime.now()
            )
            db.session.add(nuevo_doc)

        db.session.commit()
        flash("Documentos guardados exitosamente.", "success")
        return redirect(url_for("usuario.registro_completo"))

    docs = Docs.query.filter_by(id_usuario=current_user.id).order_by(Docs.fecha_actualizacion.desc()).all()
    return render_template("usuario/documentos.html", form=form, docs=docs, paso_anterior="discapacidades")




### vacantes consultas sql filtros 
@usuario_bp.route('/vacantes', methods=["GET"])
@login_required
def vacantes():
    categoria = request.args.get("categoria", "")
    estado = request.args.get("estado", "abierto")   # por defecto solo muestra abiertas
    busqueda = request.args.get("q", "")

    query = vacante.query.filter_by(estado=estado)

    if categoria:
        query = query.filter_by(area=categoria)

    if busqueda:
        query = query.filter(vacante.titulo.ilike(f"%{busqueda}%"))

    vacantes = query.order_by(vacante.fecha_publicacion.desc()).all()

    return render_template("usuario/vacantes.html", vacantes=vacantes)

@usuario_bp.route("/vacantes/<int:id>/postular", methods=["POST"])
@login_required
def postular(id):
    vac = vacante.query.get_or_404(id)

    # Evitar que el usuario se postule dos veces a la misma vacante
    ya_postulado = postulacion.query.filter_by(
        id_usuario=current_user.id,
        id_vacante=id
    ).first()

    if ya_postulado:
        flash("Ya te has postulado a esta vacante.", "warning")
        return redirect(url_for("usuario.vacantes"))

    if vac.estado != "abierto":
        flash("Esta vacante ya no está disponible.", "danger")
        return redirect(url_for("usuario.vacantes"))

    nueva_postulacion = postulacion(
        id_usuario=current_user.id,
        id_vacante=id,
        estado="postulado"
    )

    db.session.add(nueva_postulacion)
    db.session.commit()

    flash("¡Te has postulado correctamente!", "success")
    return redirect(url_for("usuario.vacantes"))
    





