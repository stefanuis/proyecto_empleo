
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    abort
    
)

import io
import zipfile
import os
import json
from sqlalchemy import exists
from sqlalchemy import case
from sqlalchemy import func
import plotly.graph_objects as go
import plotly.graph_objects as gopip 
from datetime import date,timedelta
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.user import User
from sqlalchemy import or_
from app.models.vacante import Vacante
from app.forms.vacante import VacanteForm
from app.models.postulacion import Postulacion
from app.models.personal import Personal
from app.models.contacto import Contacto
from app.models.academica import Info_academica
from app.models.personal import Personal
from app.models.familiar import Familiar
from app.models.referencias import Referencias
from app.forms.postulacion import PostulacionForm
from app.models.experiencia import Experiencia
from app.forms.experiencia import experienciaForm
from app.models.funcion_experiencia import FuncionExperiencia
from app.models.citacion import Citaciones
from app.forms.citaciones import CitacionForm
from app.utils.generar_pdf import generar_pdf_expediente
from flask_mail import Message
from app.extensions import db, mail


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

        #####  tarjetas de graficos

        hoy = datetime.now()

        inicio_semana = hoy - timedelta(days=hoy.weekday())

        inicio_semana_pasada = inicio_semana - timedelta(days=7)

        fin_semana_pasada = inicio_semana

        total_vacantes_activas = Vacante.query.filter_by(
            estado='Activa'
        ).count()


        vacantes_esta_semana = Vacante.query.filter(
            Vacante.fecha_publicacion >= inicio_semana
        ).count()


        total_hojas = Postulacion.query.count()


        hojas_esta_semana = Postulacion.query.filter(
            Postulacion.fecha_postulacion >= inicio_semana
        ).count()



        total_entrevistas = Postulacion.query.filter_by(
            estado='Entrevista'
        ).count()


        entrevistas_semana_pasada = Postulacion.query.filter(
            Postulacion.estado == 'Entrevista',
            Postulacion.fecha_postulacion >= inicio_semana_pasada,
            Postulacion.fecha_postulacion < fin_semana_pasada
        ).count()

        fecha_limite = hoy + timedelta(days=7)


        vacantes_por_cerrar = Vacante.query.filter(
            Vacante.estado == 'Activa',
            Vacante.fecha_cierre >= hoy,
            Vacante.fecha_cierre <= fecha_limite
        ).order_by(
            Vacante.fecha_cierre.asc()
        ).all()


        total_por_cerrar = len(vacantes_por_cerrar)

        dias_para_cierre = None

        if vacantes_por_cerrar:

            fecha_cierre_mas_cercana = vacantes_por_cerrar[0].fecha_cierre

            dias_para_cierre = (
            fecha_cierre_mas_cercana.date() - hoy.date()
        ).days

        ########## GRAFICOS 
        resultados = (
        db.session.query(Vacante.titulo, func.count(Postulacion.id))
        .join(Postulacion, Postulacion.id_vacante == Vacante.id)
        .group_by(Vacante.titulo)
        .order_by(func.count(Postulacion.id).desc())
        .all()
        )
 
        vacantes = [r[0] for r in resultados]
        cantidades = [r[1] for r in resultados]
 
        fig = go.Figure(data=[
            go.Bar(x=vacantes, y=cantidades, marker_color='#e6007a', width=0.4)
        ])
 
        fig.update_layout(
        title='Postulaciones por vacante',
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(
            gridcolor='#eee',
            tickmode='linear',   
            dtick=1,             
        ),
        xaxis=dict(showgrid=False),
        margin=dict(l=40, r=40, t=60, b=40),
)
        grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        return render_template(
            'admin/principal.html',
            grafico_html=grafico_html,
            vacantes_labels=vacantes_labels,
            vacantes_data=vacantes_data,
            total_vacantes_activas=total_vacantes_activas,
            vacantes_esta_semana=vacantes_esta_semana,
            total_hojas=total_hojas,
            hojas_esta_semana=hojas_esta_semana,
            total_entrevistas=total_entrevistas,
            entrevistas_semana_pasada=entrevistas_semana_pasada,
            total_por_cerrar=total_por_cerrar,
            dias_para_cierre=dias_para_cierre,
            fecha_hoy=fecha_hoy
        )
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")

@admin_bp.route("/vacantes")
@login_required
def listar_vacantes():
    if session.get("rol") != "admin":
        return "No tienes permiso para acceder a esta página", 403

    accion = request.args.get("accion", "")
    q = request.args.get("q", "").strip()
    area = request.args.get("area", "").strip()
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    vacante_id = request.args.get("vacantes", "").strip()
    nivel = request.args.get("nivel", "").strip()
    estado = request.args.get("estado", "").strip()
    fecha_desde = request.args.get("fecha_publicacion_desde", "").strip()
    fecha_hasta = request.args.get("fecha_publicacion_hasta", "").strip()
    

    todas_las_vacantes = Vacante.query.order_by(Vacante.titulo.asc()).all()

    query = Vacante.query

    if accion == "buscar":
        if q:
            query = query.filter(Vacante.titulo.ilike(f"%{q}%"))

    elif accion == "filtrar":
        if area:
            query = query.filter(Vacante.area == area)

        if area_aplicacion:
            query = query.filter(
                Vacante.area_aplicacion == area_aplicacion
            )

        if vacante_id:
            try:
                query = query.filter(Vacante.id == int(vacante_id))
            except ValueError:
                pass

        if nivel:
            query = query.filter(Vacante.nivel_academico == nivel)

        if estado:
            query = query.filter(Vacante.estado == estado)

        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
                query = query.filter(
                    Vacante.fecha_publicacion >= fecha_desde_dt
                )
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                fecha_hasta_dt += timedelta(days=1)
                query = query.filter(
                    Vacante.fecha_publicacion < fecha_hasta_dt
                )
            except ValueError:
                pass

    vacantes = query.order_by(
        Vacante.fecha_publicacion.desc()
    ).all()

    areas_aplicacion = VacanteForm.area_aplicacion.kwargs["choices"]

    return render_template(
        "admin/listar_vacante.html",
        vacantes=vacantes,
        todas_las_vacantes=todas_las_vacantes,
        areas=areas_aplicacion,
        q=q,
        area_seleccionada=area,
        area_aplicacion_seleccionada=area_aplicacion,
        vacante_seleccionada=vacante_id,
        nivel_seleccionado=nivel,
        estado_seleccionado=estado,
        fecha_publicacion_desde_valor=fecha_desde,
        fecha_publicacion_hasta_valor=fecha_hasta
    )



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
                 numero_plazas=form.numero_plazas.data,
                requiere_video=form.requiere_video.data,
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

@admin_bp.route("/vacantes/<int:id>/postulantes", methods=["GET"])
@login_required
def listar_postulantes(id):
    if session.get("rol") != "admin":
        return "No tienes permiso para acceder a esta página", 403

    vacante = Vacante.query.get_or_404(id)

    estado = request.args.get('estado', '').strip()
    experiencia_minima = request.args.get('experiencia_minima', '').strip()
    nivel_estudios = request.args.get('nivel_estudios', '').strip()
    titulo_estudios = request.args.get('titulo_estudios', '').strip()
    funcion_buscar = request.args.get('funcion', '').strip()

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


    if experiencia_minima:
        try:
            experiencia_minima_float = float(experiencia_minima)

            fecha_fin_efectiva = case(
                (Experiencia.actual == True, date.today()),
                else_=Experiencia.fecha_salida
            )

            duracion_anios = (
                func.datediff(fecha_fin_efectiva, Experiencia.fecha_ingreso) / 365.25
            )

            subq_experiencia = db.session.query(
                Experiencia.id_usuario
            ).group_by(
                Experiencia.id_usuario
            ).having(
                func.sum(duracion_anios) >= experiencia_minima_float
            ).subquery()

            query = query.filter(
                Postulacion.id_usuario.in_(db.session.query(subq_experiencia.c.id_usuario))
            )

        except ValueError:
            pass


    if nivel_estudios:
        subq_nivel = db.session.query(
            Info_academica.id_usuario
        ).filter(
            Info_academica.nivel == nivel_estudios
        ).subquery()

        query = query.filter(
            Postulacion.id_usuario.in_(db.session.query(subq_nivel.c.id_usuario))
        )

    if titulo_estudios:
        subq_titulo = db.session.query(
            Info_academica.id_usuario
        ).filter(
            Info_academica.titulo.ilike(f"%{titulo_estudios}%")
        ).subquery()

        query = query.filter(
            Postulacion.id_usuario.in_(db.session.query(subq_titulo.c.id_usuario))
        )


    if funcion_buscar:
        subq_funcion = db.session.query(
            Experiencia.id_usuario
        ).join(
            FuncionExperiencia,
            FuncionExperiencia.id_experiencia == Experiencia.id
        ).filter(
            FuncionExperiencia.funcion.ilike(f"%{funcion_buscar}%")
        ).subquery()

        query = query.filter(
            Postulacion.id_usuario.in_(db.session.query(subq_funcion.c.id_usuario))
        )

    postulaciones = query.order_by(Postulacion.fecha_postulacion.desc()).all()

    return render_template(
        "admin/listar_postulantes.html",
        vacante=vacante,
        postulaciones=postulaciones,
        estado_seleccionado=estado,
        experiencia_seleccionada=experiencia_minima,
        nivel_estudios_seleccionado=nivel_estudios,
        titulo_estudios_seleccionado=titulo_estudios,
        funcion_seleccionada=funcion_buscar
    )


    

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
    
@admin_bp.route('/admin/postulantes/<int:id>/descargar-expediente')
@login_required
def descargar_expediente(id):

     post = Postulacion.query.get_or_404(id)

     personal = Personal.query.filter_by(
            id_usuario=post.id_usuario
        ).first_or_404()

     vacante = Vacante.query.get_or_404(
            post.id_vacante
        )

     contacto = Contacto.query.filter_by(
            id_usuario=post.id_usuario
        ).first()

     academica = Info_academica.query.filter_by(
                 id_usuario=post.id_usuario
             ).first()

     buffer = generar_pdf_expediente(personal, vacante, post, contacto, academica)

     return send_file(
        buffer,
        as_attachment=True,
        download_name=f'expediente_{personal.nombres}_{personal.apellidos}.pdf',
        mimetype='application/pdf'
    )

@admin_bp.route('/admin/hoja-de-vida')
@login_required
def listar_hoja_vida():

    # 1. Filtros que llegan por la URL
    vacante_id = request.args.get('vacante_id')
    estado = request.args.get('estado')

    # 2. Obtener todas las vacantes
    vacantes = Vacante.query.all()

    # 3. Consulta de postulaciones
    query = Postulacion.query

    if vacante_id:
        query = query.filter(
            Postulacion.id_vacante == int(vacante_id)
        )

    if estado:
        query = query.filter(
            Postulacion.estado == estado
        )

    # 4. Obtener las postulaciones
    postulantes = query.order_by(
        Postulacion.fecha_postulacion.desc()
    ).all()

    # 5. Asociar la información personal a cada postulación
    for post in postulantes:

        post.personal = Personal.query.filter_by(
            id_usuario=post.id_usuario
        ).first()

    # 6. Enviar los datos a la plantilla
    return render_template(
        'listar_hojas de vida.html',
        vacantes=vacantes,
        postulantes=postulantes,
        vacante_seleccionada=vacante_id,
        estado_seleccionado=estado
    )

@admin_bp.route('/admin/expedientes/descargar-zip')
@login_required
def descargar_expedientes_zip():
    # El template envía varios checkboxes con name="ids", así que
    # llegan como ?ids=3&ids=7&ids=12
    ids = [int(i) for i in request.args.getlist('ids') if i.isdigit()]

    if not ids:
        abort(400, description='No se seleccionaron postulantes.')

    postulantes = Postulacion.query.filter(Postulacion.id.in_(ids)).all()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for post in postulantes:
            personal = post.personal
            vacante = post.vacante
            contacto = getattr(post, 'contacto', None)
            academica = getattr(post, 'academica', None)
            familiar = getattr(post, 'familiar', None)
            referencias = getattr(post, 'referencias', None)

            pdf_buffer = generar_pdf_expediente(
                personal, vacante, post, contacto, academica, familiar, referencias
            )

            nombre_archivo = f"expediente_{personal.nombres}_{personal.apellidos}_{post.id}.pdf"
            zf.writestr(nombre_archivo, pdf_buffer.read())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='expedientes.zip',
        mimetype='application/zip',
    )

#### Gestion de envio de citaciones ########

def enviar_correo_citacion(email, nombres, fecha, hora, lugar, mensaje):
    try:
        msg = Message(
            subject='Has sido citado a entrevista',
            sender='noresponder@clinpanamericana.com',  # ajusta al remitente real
            recipients=[email]
        )
        msg.attach(
            filename="logo_color.png",
            content_type="image/png",
            data=open("app/static/img/logo_color.png", "rb").read(),
            disposition="inline",
            headers={"Content-ID": "<logo_color>"}
        )
        msg.html = render_template("citacion.html", nombres=nombres, fecha=fecha, hora=hora, lugar=lugar,mensaje=mensaje,)
        mail.send(msg)
        return True
    except Exception as e:
        print("ERROR SMTP al enviar citación:")
        print(type(e))
        print(str(e))
        return False


@admin_bp.route("admin/citaciones")
@login_required
def listar_citaciones():

    q = request.args.get('q', '').strip()
    vacante_id = request.args.get('vacante_id')
    estados_seleccionados = request.args.getlist('estado')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    vacantes = Vacante.query.all()

    # Citaciones no tiene relationship() hacia Postulacion/User/Vacante,
    # así que seleccionamos las 4 entidades unidas explícitamente
    query = (
        db.session.query(Citaciones, Postulacion, User, Vacante)
        .join(Postulacion, Citaciones.id_postulacion == Postulacion.id)
        .join(User, Postulacion.id_usuario == User.id)
        .join(Vacante, Postulacion.id_vacante == Vacante.id)
    )

    if q:
        busqueda = f"%{q}%"
        query = query.filter(
            (User.nombres.ilike(busqueda)) | (User.apellidos.ilike(busqueda))
        )

    if vacante_id:
        query = query.filter(Postulacion.id_vacante == int(vacante_id))

    if fecha_desde:
        query = query.filter(Citaciones.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())

    if fecha_hasta:
        query = query.filter(Citaciones.fecha <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())

    if estados_seleccionados:
        condiciones = []
        if 'confirmada' in estados_seleccionados:
            condiciones.append(Citaciones.respuesta == 'confirmada')
        if 'rechazada' in estados_seleccionados:
            condiciones.append(Citaciones.respuesta == 'rechazada')
        if 'sin_responder' in estados_seleccionados:
            condiciones.append(Citaciones.respuesta.is_(None))

        if condiciones:
            query = query.filter(or_(*condiciones))

    citaciones = query.order_by(Citaciones.fecha.desc()).all()

    return render_template(
        'admin/citaciones.html',
        citaciones=citaciones,
        vacantes=vacantes,
        q=q,
        vacante_seleccionada=vacante_id,
        estados_seleccionados=estados_seleccionados,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

@admin_bp.route('/admin/vacantes/<int:id>/citar-seleccionados', methods=['POST'])
@login_required
def citar_seleccionados(id):
    datos_raw = request.form.get('postulaciones_seleccionadas')
 
    if not datos_raw:
        flash('No seleccionaste ningún postulante.', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))
 
    datos = json.loads(datos_raw)
    ids = datos.get('ids', [])
    fecha = datos.get('fecha')
    hora = datos.get('hora')
    lugar = datos.get('lugar') or 'Por confirmar'
    mensaje = datos.get('mensaje') or ''
 
    if not ids or not fecha or not hora:
        flash('Faltan datos para citar (fecha, hora o postulantes).', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))
 
    postulaciones = Postulacion.query.filter(Postulacion.id.in_(ids)).all()
 
    enviados = 0
    fallidos = 0
 
    for post in postulaciones:
        candidato = post.candidato  
 
        exito = enviar_correo_citacion(
            email=candidato.correo,        
            nombres=candidato.nombres,
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            mensaje=mensaje,
        )
 
        if exito:
            post.estado = 'Entrevista'
            enviados += 1
        else:
            fallidos += 1
 
    db.session.commit()
 
    if fallidos == 0:
        flash(f'Se citó a {enviados} postulante(s) correctamente.', 'success')
    else:
        flash(f'Se citó a {enviados} postulante(s). {fallidos} correo(s) no se pudieron enviar.', 'warning')
 
    return redirect(url_for('admin.listar_postulantes', id=id))
 


