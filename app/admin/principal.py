
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    abort,
    current_app,
    jsonify,
)
import secrets
import io
import zipfile
import os
import json
from sqlalchemy import exists
from sqlalchemy import func
import plotly.graph_objects as go
from datetime import date,timedelta
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.user import User
from sqlalchemy import or_
from app.models.vacante import Vacante
from app.models.vacante_funcion import VacanteFuncion
from app.forms.vacante import VacanteForm
from app.models.postulacion import Postulacion
from app.models.personal import Personal
from app.models.perfil_profesional import PerfilProfesional
from app.models.perfil_funcion import PerfilFuncion
from app.models.funcion_area import FuncionArea
from app.models.academica import Info_academica
from app.models.cursos import Cursos
from app.models.referencias_personales import ReferenciasPersonales
from app.models.discapacidades import Discapacidades
from app.models.referencias import Referencias
from app.forms.postulacion import PostulacionForm
from app.models.experiencia import Experiencia
from app.models.citacion import Citaciones
from app.forms.citaciones import CitacionForm
from app.models.docs import OtrosDocumentos
from app.utils.generar_pdf import generar_pdf_expediente
from app.utils.funciones import (
    funciones_activas_por_area,
    funciones_de_candidatos,
    funciones_de_vacante,
    funciones_validas_para_area,
    guardar_funciones_vacante,
    resumen_coincidencia,
)
from app.utils.perfil import (
    DIAS_POR_ANIO,
    calcular_completitud_perfil,
    dias_experiencia_por_usuario,
    formatear_experiencia,
    obtener_experiencia_total,
    obtener_nivel_mas_alto,
)
from app.extensions import db
from app.utils.correo import enviar_correo
from app.utils.archivos import ruta_absoluta
from app.utils.historial import historial_de, registrar_evento
from app.constantes import ESTADOS_POSTULACION, MENSAJES_CAMBIO_ESTADO
from app.utils.permisos import exigir_rol


from . import admin_bp


@admin_bp.before_request
def verificar_admin():
    # Protege TODAS las rutas del blueprint, incluidas las que se agreguen después
    return exigir_rol("admin")



DIAS_SIN_REVISAR = 3


def _pendientes_dashboard():
    """Lo que el reclutador debe atender hoy, con el enlace a la lista filtrada."""
    hoy = date.today()
    inicio_hoy = datetime.combine(hoy, datetime.min.time())
    fin_semana = hoy + timedelta(days=6 - hoy.weekday())
    citaciones_vigentes = Citaciones.query.filter(
        or_(Citaciones.respuesta.is_(None), Citaciones.respuesta != 'rechazada')
    )

    return [
        {
            "titulo": "Postulaciones sin revisar",
            "detalle": f"En estado Postulado hace más de {DIAS_SIN_REVISAR} días",
            "cantidad": Postulacion.query.filter(
                Postulacion.estado == 'postulado',
                Postulacion.fecha_postulacion < hoy - timedelta(days=DIAS_SIN_REVISAR),
            ).count(),
            "url": url_for('admin.listar_hoja_vida', estado='postulado'),
        },
        {
            "titulo": "Entrevistas hoy",
            "detalle": "Citaciones programadas para hoy",
            "cantidad": citaciones_vigentes.filter(Citaciones.fecha == hoy).count(),
            "url": url_for('admin.listar_citaciones', fecha_desde=hoy.isoformat(), fecha_hasta=hoy.isoformat()),
        },
        {
            "titulo": "Entrevistas esta semana",
            "detalle": f"Hasta el {fin_semana.strftime('%d/%m')}",
            "cantidad": citaciones_vigentes.filter(
                Citaciones.fecha >= hoy, Citaciones.fecha <= fin_semana
            ).count(),
            "url": url_for('admin.listar_citaciones', fecha_desde=hoy.isoformat(), fecha_hasta=fin_semana.isoformat()),
        },
        {
            "titulo": "Citaciones sin respuesta",
            "detalle": "Entrevistas próximas que el candidato no ha confirmado",
            "cantidad": Citaciones.query.filter(
                Citaciones.respuesta.is_(None), Citaciones.fecha >= hoy
            ).count(),
            "url": url_for('admin.listar_citaciones', estado='sin_responder', fecha_desde=hoy.isoformat()),
        },
        {
            "titulo": "Vacantes con cierre vencido",
            "detalle": "Siguen activas pero ya pasó su fecha de cierre",
            "cantidad": Vacante.query.filter(
                Vacante.estado == 'Activa', Vacante.fecha_cierre < inicio_hoy
            ).count(),
            "url": url_for('admin.listar_vacantes', vencidas='1'),
        },
        {
            "titulo": "Vacantes sin funciones",
            "detalle": "Activas sin funciones del cargo: no se ordenan por coincidencia",
            "cantidad": Vacante.query.filter(
                Vacante.estado == 'Activa',
                ~exists().where(VacanteFuncion.id_vacante == Vacante.id),
            ).count(),
            "url": url_for('admin.listar_vacantes', sin_funciones='1'),
        },
    ]


@admin_bp.route("/principal", methods=["GET"])
@login_required
def inicial():
    if(session["rol"] == "admin"):
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
            estado='entrevista'
        ).count()


        entrevistas_semana_pasada = Postulacion.query.filter(
            Postulacion.estado == 'entrevista',
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
            pendientes=_pendientes_dashboard(),
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
# Asegúrate de tener estos imports arriba de principal.py:
# from sqlalchemy import func
# from datetime import datetime, timedelta


@admin_bp.route("/vacantes")
@login_required
def listar_vacantes():
    if session.get("rol") != "admin":
        return "No tienes permiso para acceder a esta página", 403

    q = request.args.get("q", "").strip()
    area = request.args.get("area", "").strip()
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    vacante_id = request.args.get("vacantes", "").strip()
    nivel = request.args.get("nivel", "").strip()
    estado = request.args.get("estado", "").strip()
    fecha_desde = request.args.get("fecha_publicacion_desde", "").strip()
    fecha_hasta = request.args.get("fecha_publicacion_hasta", "").strip()

    page = request.args.get("page", 1, type=int)
    per_page = 15
    # Accesos directos desde los pendientes del dashboard
    solo_vencidas = request.args.get("vencidas") == "1"
    solo_sin_funciones = request.args.get("sin_funciones") == "1"

    todas_las_vacantes = Vacante.query.order_by(Vacante.titulo.asc()).all()

    query = Vacante.query

    if solo_vencidas:
        query = query.filter(
            Vacante.estado == 'Activa',
            Vacante.fecha_cierre < datetime.combine(date.today(), datetime.min.time()),
        )
    if solo_sin_funciones:
        query = query.filter(
            Vacante.estado == 'Activa',
            ~exists().where(VacanteFuncion.id_vacante == Vacante.id),
        )

    # El texto buscado y los filtros se aplican juntos
    if q:
        query = query.filter(Vacante.titulo.ilike(f"%{q}%"))

    if area:
        query = query.filter(Vacante.area == area)

    if area_aplicacion:
        query = query.filter(Vacante.area_aplicacion == area_aplicacion)

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
            query = query.filter(Vacante.fecha_publicacion >= fecha_desde_dt)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            fecha_hasta_dt += timedelta(days=1)
            query = query.filter(Vacante.fecha_publicacion < fecha_hasta_dt)
        except ValueError:
            pass

    # ---- Paginación en SQL (el id desempata para que el orden sea estable) ----
    query = query.order_by(Vacante.fecha_publicacion.desc(), Vacante.id.desc())
    paginado = db.paginate(query, page=page, per_page=per_page, error_out=False)
    vacantes = paginado.items

    pagination = {
        "page": paginado.page,
        "pages": paginado.pages,
        "total": paginado.total,
        "has_prev": paginado.has_prev,
        "has_next": paginado.has_next,
        "prev_num": paginado.prev_num,
        "next_num": paginado.next_num,
    }

    # ---- Cantidad de postulaciones por vacante (solo las de esta página) ----
    ids_pagina = [v.id for v in vacantes]
    conteos = {}
    if ids_pagina:
        conteos = dict(
            db.session.query(Postulacion.id_vacante, func.count(Postulacion.id))
            .filter(Postulacion.id_vacante.in_(ids_pagina))
            .group_by(Postulacion.id_vacante)
            .all()
        )

    areas_aplicacion = VacanteForm.area_aplicacion.kwargs["choices"]
    # Mismos valores que guarda el formulario de vacantes
    niveles = [v for v, _ in VacanteForm.nivel_academico.kwargs["choices"] if v]

    return render_template(
        "admin/listar_vacante.html",
        niveles=niveles,
        vacantes=vacantes,
        pagination=pagination,
        conteos=conteos,
        todas_las_vacantes=todas_las_vacantes,
        areas=areas_aplicacion,
        q=q,
        area_seleccionada=area,
        area_aplicacion_seleccionada=area_aplicacion,
        vacante_seleccionada=vacante_id,
        nivel_seleccionado=nivel,
        estado_seleccionado=estado,
        fecha_publicacion_desde_valor=fecha_desde,
        fecha_publicacion_hasta_valor=fecha_hasta,
        solo_vencidas=solo_vencidas,
        solo_sin_funciones=solo_sin_funciones,
    )



@admin_bp.route("/funciones-area", methods=["GET"])
@login_required
def funciones_area():
    """Catálogo de funciones de un área, para el selector de la vacante."""
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    return jsonify({
        "funciones": [
            {"id": funcion.id, "nombre": funcion.nombre}
            for funcion in funciones_activas_por_area(area_aplicacion)
        ]
    })


def _render_formulario_vacante(form, funciones_seleccionadas, error_funciones=None):
    return render_template(
        "admin/crear_vacantes.html",
        form=form,
        funciones_seleccionadas=sorted(funciones_seleccionadas),
        error_funciones=error_funciones,
    )


def _ids_funciones_enviadas():
    return {int(v) for v in request.form.getlist("funciones") if v.isdigit()}


@admin_bp.route("/vacantes/crear", methods=["GET", "POST"])
@login_required
def crear_vacante():
    form = VacanteForm()
    error_funciones = None

    if form.validate_on_submit():
        funciones, error_funciones = funciones_validas_para_area(
            form.area_aplicacion.data,
            request.form.getlist("funciones"),
        )
        if not error_funciones:
            nueva_vacante = Vacante(
                titulo=form.titulo.data,
                area=form.area.data,
                area_aplicacion=form.area_aplicacion.data,
                nivel_academico=form.nivel_academico.data,
                descripcion=form.descripcion.data,
                requisito=form.requisito.data,
                salario=form.salario.data,
                estado=form.estado.data,
                fecha_publicacion=form.fecha_publicacion.data or date.today(),
                fecha_cierre=form.fecha_cierre.data,
                numero_plazas=form.numero_plazas.data,
                requiere_video=form.requiere_video.data,
                id_usuario_creador=current_user.id
            )
            db.session.add(nueva_vacante)
            db.session.flush()
            guardar_funciones_vacante(nueva_vacante.id, funciones)
            db.session.commit()

            flash("Vacante creada correctamente.", "success")
            return redirect(url_for("admin.listar_vacantes"))

    return _render_formulario_vacante(
        form,
        _ids_funciones_enviadas() if request.method == "POST" else set(),
        error_funciones,
    )


@admin_bp.route("/vacantes/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_vacante(id):
    vacante = Vacante.query.get_or_404(id)
    form = VacanteForm(obj=vacante)
    error_funciones = None

    if form.validate_on_submit():
        funciones, error_funciones = funciones_validas_para_area(
            form.area_aplicacion.data,
            request.form.getlist("funciones"),
        )
        if not error_funciones:
            form.populate_obj(vacante)   # copia los datos del form al objeto
            if not vacante.fecha_publicacion:
                vacante.fecha_publicacion = date.today()
            guardar_funciones_vacante(vacante.id, funciones)
            db.session.commit()
            flash("Vacante actualizada correctamente.", "success")
            return redirect(url_for("admin.listar_vacantes"))

    if request.method == "POST":
        seleccionadas = _ids_funciones_enviadas()
    else:
        seleccionadas = {funcion.id for funcion in funciones_de_vacante(vacante.id)}

    return _render_formulario_vacante(form, seleccionadas, error_funciones)  # reutiliza el mismo template


@admin_bp.route("/vacantes/<int:id>/cambiar-estado", methods=["POST"])
@login_required
def cambiar_estado_vacante(id):
    if session.get("rol") != "admin":
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.", 403)

    vacante = Vacante.query.get_or_404(id)

    if vacante.estado == 'Activa':
        vacante.estado = 'Cerrada'
        flash(f'La vacante "{vacante.titulo}" fue cerrada.', 'success')
    else:
        cierre = vacante.fecha_cierre
        if cierre and (cierre.date() if isinstance(cierre, datetime) else cierre) < date.today():
            flash(
                f'La vacante "{vacante.titulo}" tiene la fecha de cierre vencida. '
                'Edítala y pon una nueva fecha de cierre para reabrirla.',
                'warning',
            )
            return redirect(request.referrer or url_for('admin.listar_vacantes'))
        vacante.estado = 'Activa'
        flash(f'La vacante "{vacante.titulo}" fue reabierta.', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('admin.listar_vacantes'))

@admin_bp.route("/vacantes/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_vacante(id):
    if session.get("rol") != "admin":
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.", 403)

    vacante = Vacante.query.get_or_404(id)

    total = Postulacion.query.filter_by(id_vacante=id).count()
    if total > 0:
        flash(f'No se puede eliminar "{vacante.titulo}": tiene {total} postulación(es). '
              'Ciérrala en su lugar.', 'error')
        return redirect(url_for('admin.listar_vacantes'))

    titulo = vacante.titulo
    VacanteFuncion.query.filter_by(id_vacante=id).delete(synchronize_session=False)
    db.session.delete(vacante)
    db.session.commit()
    flash(f'La vacante "{titulo}" fue eliminada.', 'success')
    return redirect(url_for('admin.listar_vacantes'))


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

    # ---- Funciones del cargo y coincidencia con cada candidato ----
    funciones_vacante = funciones_de_vacante(id)
    ids_funciones_vacante = [funcion.id for funcion in funciones_vacante]
    funciones_filtro = {
        int(valor) for valor in request.args.getlist('funciones') if valor.isdigit()
    } & set(ids_funciones_vacante)
    modo_funciones = request.args.get('modo_funciones', 'alguna')
    if modo_funciones not in ('alguna', 'todas'):
        modo_funciones = 'alguna'

    page = request.args.get('page', 1, type=int)
    per_page = 15

    # Cuántas funciones del cargo tiene cada candidato en su perfil
    subq_coincidencia = db.session.query(
        PerfilFuncion.id_usuario.label('id_usuario'),
        func.count(PerfilFuncion.id).label('cantidad'),
    ).filter(
        PerfilFuncion.id_funcion.in_(ids_funciones_vacante)
    ).group_by(
        PerfilFuncion.id_usuario
    ).subquery()
    coincidencia = func.coalesce(subq_coincidencia.c.cantidad, 0)

    query = db.session.query(
        Postulacion,
        Personal,
        coincidencia,
    ).join(
        Personal,
        Personal.id_usuario == Postulacion.id_usuario
    ).outerjoin(
        subq_coincidencia,
        subq_coincidencia.c.id_usuario == Postulacion.id_usuario
    ).filter(
        Postulacion.id_vacante == id
    )
 
    if estado:
        query = query.filter(Postulacion.estado == estado)
 
    if experiencia_minima:
        try:
            minimo_dias = float(experiencia_minima) * DIAS_POR_ANIO
        except ValueError:
            minimo_dias = None

        if minimo_dias is not None:
            # Mismo cálculo que la columna "Experiencia" de la tabla
            ids_postulantes = [
                id_usuario
                for (id_usuario,) in db.session.query(Postulacion.id_usuario)
                .filter(Postulacion.id_vacante == id)
                .distinct()
            ]
            dias_por_usuario = dias_experiencia_por_usuario(ids_postulantes)
            ids_cumplen = [
                id_usuario
                for id_usuario, dias in dias_por_usuario.items()
                if dias >= minimo_dias
            ]
            query = query.filter(Postulacion.id_usuario.in_(ids_cumplen))
 
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
 
    if funciones_filtro:
        subq_funciones = db.session.query(
            PerfilFuncion.id_usuario
        ).filter(
            PerfilFuncion.id_funcion.in_(funciones_filtro)
        ).group_by(
            PerfilFuncion.id_usuario
        )
        if modo_funciones == 'todas':
            subq_funciones = subq_funciones.having(
                func.count(func.distinct(PerfilFuncion.id_funcion)) == len(funciones_filtro)
            )
        query = query.filter(Postulacion.id_usuario.in_(subq_funciones))

    # Búsqueda por texto: solo para vacantes antiguas sin funciones definidas
    if funcion_buscar and not funciones_vacante:
        # Las funciones del candidato se registran en su Perfil profesional
        subq_funcion = db.session.query(
            PerfilFuncion.id_usuario
        ).join(
            FuncionArea,
            FuncionArea.id == PerfilFuncion.id_funcion
        ).filter(
            FuncionArea.nombre.ilike(f"%{funcion_buscar}%")
        ).subquery()
 
        query = query.filter(
            Postulacion.id_usuario.in_(db.session.query(subq_funcion.c.id_usuario))
        )
 
    # ---- Paginación en SQL ----
    # Primero los que más funciones del cargo cumplen; el id desempata
    # fechas iguales para que el orden entre páginas sea estable.
    query = query.order_by(
        coincidencia.desc(),
        Postulacion.fecha_postulacion.desc(),
        Postulacion.id.desc(),
    )

    total = query.count()
    total_paginas = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_paginas))   # evita páginas fuera de rango
 
    resultados = query.offset((page - 1) * per_page).limit(per_page).all()
 
    pagination = {
        'page': page,
        'pages': total_paginas,
        'total': total,
        'has_prev': page > 1,
        'has_next': page < total_paginas,
        'prev_num': page - 1,
        'next_num': page + 1,
    }
 
    # Nivel, experiencia y funciones cumplidas solo para las filas de la página actual
    funciones_por_candidato = funciones_de_candidatos(
        [postulacion.id_usuario for postulacion, _personal, _cantidad in resultados],
        ids_funciones_vacante,
    )
    postulaciones = []
    for postulacion, personal, _cantidad in resultados:
        nivel = obtener_nivel_mas_alto(postulacion.id_usuario)
        experiencia_anos = obtener_experiencia_total(postulacion.id_usuario)
        experiencia_texto = formatear_experiencia(experiencia_anos)
        resumen = resumen_coincidencia(
            funciones_vacante,
            funciones_por_candidato[postulacion.id_usuario],
        )
        postulaciones.append((postulacion, personal, nivel, experiencia_texto, resumen))

    return render_template(
        "admin/listar_postulantes.html",
        vacante=vacante,
        postulaciones=postulaciones,
        pagination=pagination,
        estado_seleccionado=estado,
        experiencia_seleccionada=experiencia_minima,
        nivel_estudios_seleccionado=nivel_estudios,
        titulo_estudios_seleccionado=titulo_estudios,
        funcion_seleccionada=funcion_buscar,
        funciones_vacante=funciones_vacante,
        funciones_filtro=funciones_filtro,
        modo_funciones=modo_funciones,
    )
 

@admin_bp.route('/postulacion/<int:id>/documentos/descargar-zip')
@login_required
def descargar_documentos_candidato(id):
    post = Postulacion.query.get_or_404(id)

    documentos = OtrosDocumentos.query.filter_by(
        id_usuario=post.id_usuario
    ).all()

    if not documentos:
        abort(404, description='Este candidato no tiene documentos cargados.')

    personal = Personal.query.filter_by(id_usuario=post.id_usuario).first_or_404()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for documento in documentos:
            if not documento.ruta_soporte:
                continue

            ruta = ruta_absoluta(documento.ruta_soporte)

            if ruta:
                extension = os.path.splitext(documento.ruta_soporte)[1]
                nombre_en_zip = f"{documento.tipo or 'documento'}_{documento.nombre}{extension}"
                zf.write(ruta, nombre_en_zip)

    zip_buffer.seek(0)

    nombre_zip = f"documentos_{personal.nombres}_{personal.apellidos}.zip"

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=nombre_zip,
        mimetype='application/zip',
    )

@admin_bp.route('/postulante/<int:id>/expediente')
@login_required
def ver_expediente(id):
    if(session["rol"] == "admin"):
        post = Postulacion.query.get_or_404(id)
        usuario = User.query.get_or_404(post.id_usuario)
        vacante = Vacante.query.get_or_404(post.id_vacante)

        personal = Personal.query.filter_by(id_usuario=post.id_usuario).first()
        perfil_profesional = PerfilProfesional.query.filter_by(
            id_usuario=post.id_usuario
        ).first()
        funciones_perfil = FuncionArea.query.join(
            PerfilFuncion,
            PerfilFuncion.id_funcion == FuncionArea.id,
        ).filter(
            PerfilFuncion.id_usuario == post.id_usuario,
        ).order_by(FuncionArea.nombre).all()
        academica = Info_academica.query.filter_by(id_usuario=post.id_usuario).all()
        experiencia=Experiencia.query.filter_by(id_usuario=post.id_usuario).order_by(Experiencia.fecha_ingreso.desc()).all()
        cursos=Cursos.query.filter_by(id_usuario=post.id_usuario).order_by(Cursos.fecha_realizacion.desc()).all()
        referencias = Referencias.query.filter_by(id_usuario=post.id_usuario).all()
        referencias_personales=ReferenciasPersonales.query.filter_by(id_usuario=post.id_usuario).all()
        discapacidades=Discapacidades.query.filter_by(id_usuario=post.id_usuario).all()
        documentos = OtrosDocumentos.query.filter_by(id_usuario=post.id_usuario).all()

        funciones_vacante = funciones_de_vacante(vacante.id)
        coincidencia = resumen_coincidencia(
            funciones_vacante,
            {funcion.id for funcion in funciones_perfil},
        )

        return render_template('admin/expediente.html',
                                post=post,
                                usuario=usuario,
                                vacante=vacante,
                                coincidencia=coincidencia,
                                historial=historial_de(post.id),
                                personal=personal,
                                perfil_profesional=perfil_profesional,
                                funciones_perfil=funciones_perfil,
                                academica=academica,
                                experiencia=experiencia,
                                cursos=cursos,
                                referencias=referencias,
                                referencias_personales=referencias_personales,
                                discapacidades=discapacidades,
                                documentos=documentos)
    else:
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.")

NOTAS_POR_AREA = (
    ("notas_reclutador", "reclutador"),
    ("notas_psicologia", "psicología"),
    ("notas_talento_humano", "gestión humana"),
)


def _cambiar_estado(postulacion, nuevo_estado):
    """Cambia el estado y deja el registro en el historial (no hace commit).

    Si queda contratado, retira sus otras postulaciones abiertas y devuelve
    la lista de las que retiró.
    """
    anterior = postulacion.estado
    postulacion.estado = nuevo_estado
    postulacion.fecha_actualizacion = datetime.now()
    registrar_evento(
        postulacion.id,
        f"Cambió el estado: {ESTADOS_POSTULACION.get(anterior, anterior)} "
        f"→ {ESTADOS_POSTULACION[nuevo_estado]}",
    )

    retiradas = []
    if nuevo_estado == 'contratado':
        vacante = db.session.get(Vacante, postulacion.id_vacante)
        retiradas = Postulacion.query.filter(
            Postulacion.id_usuario == postulacion.id_usuario,
            Postulacion.id != postulacion.id,
            Postulacion.estado.notin_(['contratado', 'rechazado', 'retirada'])
        ).all()
        for otra in retiradas:
            otra.estado = 'retirada'
            otra.fecha_actualizacion = datetime.now()
            registrar_evento(
                otra.id,
                "Retirada automáticamente",
                f"El candidato fue contratado en la vacante \"{vacante.titulo if vacante else ''}\".",
                autor=None,
            )
    return retiradas


def _notificar_cambio_estado(postulacion, retiradas=()):
    """Correo al candidato con el nuevo estado. Devuelve True si se envió."""
    textos = MENSAJES_CAMBIO_ESTADO.get(postulacion.estado)
    candidato = db.session.get(User, postulacion.id_usuario)
    vacante = db.session.get(Vacante, postulacion.id_vacante)
    if not textos or not candidato or not candidato.correo:
        return False

    enviado = enviar_correo(
        candidato.correo,
        textos["asunto"],
        "correos/estado_postulacion.html",
        nombres=candidato.nombres,
        vacante=vacante.titulo if vacante else "",
        titulo=textos["titulo"],
        mensaje=textos["mensaje"],
        otras_retiradas=len(retiradas),
    )
    if enviado:
        registrar_evento(
            postulacion.id,
            "Se notificó al candidato por correo",
            textos["asunto"],
        )
    return enviado


@admin_bp.route("/postulacion/<int:id>/actualizar", methods=["POST"])
@login_required
def actualizar_postulacion(id):
    postulacion = Postulacion.query.get_or_404(id)

    nuevo_estado = request.form.get("estado", postulacion.estado)
    if nuevo_estado not in ESTADOS_POSTULACION:
        flash("El estado seleccionado no es válido.", "error")
        return redirect(url_for('admin.ver_expediente', id=postulacion.id))

    for campo, area in NOTAS_POR_AREA:
        nuevas = (request.form.get(campo) or "").strip()
        if nuevas != (getattr(postulacion, campo) or "").strip():
            setattr(postulacion, campo, nuevas)
            registrar_evento(postulacion.id, f"Actualizó las notas de {area}")

    retiradas = []
    cambio_estado = nuevo_estado != postulacion.estado
    if cambio_estado:
        retiradas = _cambiar_estado(postulacion, nuevo_estado)
    postulacion.fecha_actualizacion = datetime.now()
    db.session.commit()

    mensaje = "Cambios guardados."
    if retiradas:
        mensaje += f" Se retiraron {len(retiradas)} postulación(es) abiertas del candidato."
    flash(mensaje, "success")

    if cambio_estado and request.form.get("notificar") == "1" and nuevo_estado in MENSAJES_CAMBIO_ESTADO:
        if _notificar_cambio_estado(postulacion, retiradas):
            flash("Se avisó al candidato por correo.", "success")
        else:
            flash("No se pudo enviar el correo al candidato.", "warning")
        db.session.commit()

    return redirect(url_for('admin.listar_postulantes', id=postulacion.id_vacante))

@admin_bp.route("/vacantes/<int:id>/acciones-masivas", methods=["POST"])
@login_required
def acciones_masivas(id):
    """Cambios de estado sobre varios postulantes de una vacante a la vez."""
    vacante = Vacante.query.get_or_404(id)
    accion = request.form.get("accion")
    ids = {
        int(valor)
        for valor in request.form.get("ids", "").split(",")
        if valor.strip().isdigit()
    }
    volver = redirect(request.referrer or url_for('admin.listar_postulantes', id=id))

    if accion not in ("revision", "rechazar") or not ids:
        flash("Selecciona al menos un postulante y una acción válida.", "error")
        return volver

    # Solo postulaciones de esta vacante, aunque el formulario envíe otros ids
    postulaciones = Postulacion.query.filter(
        Postulacion.id.in_(ids),
        Postulacion.id_vacante == id,
    ).all()

    if accion == "revision":
        cambiadas = [p for p in postulaciones if p.estado == "postulado"]
        for postulacion in cambiadas:
            _cambiar_estado(postulacion, "revision")
        db.session.commit()
        mensaje = f"{len(cambiadas)} postulante(s) pasaron a En revisión."
        omitidas = len(postulaciones) - len(cambiadas)
        if omitidas:
            mensaje += f" {omitidas} no estaban en estado Postulado y no se cambiaron."
        flash(mensaje, "success")
        return volver

    # Rechazar y enviar correo
    cambiadas = [
        p for p in postulaciones
        if p.estado not in ("contratado", "retirada", "rechazado")
    ]
    enviados = 0
    for postulacion in cambiadas:
        _cambiar_estado(postulacion, "rechazado")
        candidato = db.session.get(User, postulacion.id_usuario)
        if candidato and candidato.correo and enviar_correo_rechazo(
            email=candidato.correo,
            nombres=candidato.nombres,
            vacante=vacante.titulo,
        ):
            postulacion.fecha_correo_rechazo = datetime.now()
            registrar_evento(postulacion.id, "Se envió el correo de rechazo al candidato")
            enviados += 1
    db.session.commit()

    mensaje = f"{len(cambiadas)} postulante(s) rechazados; {enviados} correo(s) enviados."
    omitidas = len(postulaciones) - len(cambiadas)
    if omitidas:
        mensaje += f" {omitidas} ya estaban contratados, retirados o rechazados."
    flash(mensaje, "success" if enviados == len(cambiadas) else "warning")
    return volver


@admin_bp.route('/postulantes/<int:id>/descargar-expediente')
@login_required
def descargar_expediente(id):
    if session.get("rol") != "admin":
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.", 403)

    post = Postulacion.query.get_or_404(id)
    uid = post.id_usuario
    usuario = User.query.get_or_404(uid)

    personal = Personal.query.filter_by(id_usuario=uid).first_or_404()
    vacante = Vacante.query.get_or_404(post.id_vacante)


    academica = Info_academica.query.filter_by(id_usuario=uid).all()
    referencias = Referencias.query.filter_by(id_usuario=uid).all()

    experiencia = (Experiencia.query.filter_by(id_usuario=uid)
                   .order_by(Experiencia.fecha_ingreso.desc()).all())
    cursos = (Cursos.query.filter_by(id_usuario=uid)
              .order_by(Cursos.fecha_realizacion.desc()).all())
    referencias_personales = ReferenciasPersonales.query.filter_by(id_usuario=uid).all()
    discapacidades = Discapacidades.query.filter_by(id_usuario=uid).all()

    buffer = generar_pdf_expediente(
        personal=personal,
        vacante=vacante,
        post=post,
        usuario=usuario,
        academica=academica,
        referencias=referencias,
        experiencia=experiencia,
        cursos=cursos,
        referencias_personales=referencias_personales,
        discapacidades=discapacidades,
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'Hoja_de_vida_{personal.nombres}_{personal.apellidos}.pdf',
        mimetype='application/pdf'
    )


@admin_bp.route('/hoja-de-vida')
@login_required
def listar_hoja_vida():

    # --------------------------------------------------
    # FILTROS RECIBIDOS POR GET
    # --------------------------------------------------
    vacante_id = request.args.get('vacante_id', '').strip()
    estado = request.args.get('estado', '').strip()
    q = request.args.get('q', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    nivel_academico = request.args.get('nivel_academico', '').strip()
    completitud_filtro = request.args.get('completitud', '').strip()

    # --------------------------------------------------
    # PAGINACIÓN
    # --------------------------------------------------
    page = request.args.get('page', 1, type=int)
    per_page = 15

    vacantes = Vacante.query.order_by(Vacante.titulo.asc()).all()

    # --------------------------------------------------
    # CONSULTA PRINCIPAL (con joins, sin N+1)
    # --------------------------------------------------
    query = db.session.query(Postulacion).join(
        Vacante, Vacante.id == Postulacion.id_vacante
    ).join(
        Personal, Personal.id_usuario == Postulacion.id_usuario
    )

    if vacante_id:
        try:
            query = query.filter(Postulacion.id_vacante == int(vacante_id))
        except ValueError:
            pass

    if estado:
        query = query.filter(Postulacion.estado == estado)

    if q:
        query = query.filter(
            db.or_(
                Personal.nombres.ilike(f"%{q}%"),
                Personal.apellidos.ilike(f"%{q}%"),
                Personal.num_doc.ilike(f"%{q}%")
            )
        )

    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
            query = query.filter(Postulacion.fecha_postulacion >= fecha_desde_dt)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Postulacion.fecha_postulacion < fecha_hasta_dt)
        except ValueError:
            pass

    if nivel_academico:
        subq_nivel = db.session.query(
            Info_academica.id_usuario
        ).filter(
            Info_academica.nivel == nivel_academico
        ).subquery()

        query = query.filter(
            Postulacion.id_usuario.in_(db.session.query(subq_nivel.c.id_usuario))
        )

    query = query.order_by(Postulacion.fecha_postulacion.desc())

    if completitud_filtro:
        todos = query.all()

        for post in todos:
            post.personal = Personal.query.filter_by(id_usuario=post.id_usuario).first()
            post.usuario = User.query.get(post.id_usuario)
            post.vacante = Vacante.query.get(post.id_vacante)
            post.completitud = calcular_completitud_perfil(post.id_usuario)
            post.nivel_mas_alto = obtener_nivel_mas_alto(post.id_usuario)

        if completitud_filtro == 'completo':
            filtrados = [p for p in todos if p.completitud['porcentaje'] == 100]
        else:
            filtrados = [p for p in todos if p.completitud['porcentaje'] < 100]

        total = len(filtrados)
        inicio = (page - 1) * per_page
        fin = inicio + per_page
        postulantes = filtrados[inicio:fin]

        total_paginas = max(1, (total + per_page - 1) // per_page)
        pagination = {
            'page': page,
            'pages': total_paginas,
            'total': total,
            'has_prev': page > 1,
            'has_next': page < total_paginas,
            'prev_num': page - 1,
            'next_num': page + 1,
        }

    # --------------------------------------------------
    # CASO B: sin filtro de completitud
    # Paginación real en SQL, mucho más eficiente:
    # solo calculamos completitud para los 15 de la página actual.
    # --------------------------------------------------
    else:
        paginado = db.paginate(
            query,
            page=page,
            per_page=per_page,
            error_out=False
        )

        postulantes = paginado.items

        for post in postulantes:
            post.personal = Personal.query.filter_by(id_usuario=post.id_usuario).first()
            post.usuario = User.query.get(post.id_usuario)
            post.vacante = Vacante.query.get(post.id_vacante)
            post.completitud = calcular_completitud_perfil(post.id_usuario)
            post.nivel_mas_alto = obtener_nivel_mas_alto(post.id_usuario)

        pagination = {
            'page': paginado.page,
            'pages': paginado.pages,
            'total': paginado.total,
            'has_prev': paginado.has_prev,
            'has_next': paginado.has_next,
            'prev_num': paginado.prev_num,
            'next_num': paginado.next_num,
        }

    return render_template(
        'listar_hojas_de_vida.html',
        vacantes=vacantes,
        postulantes=postulantes,
        vacante_seleccionada=vacante_id,
        estado_seleccionado=estado,
        q=q,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        nivel_academico_seleccionado=nivel_academico,
        completitud_seleccionada=completitud_filtro,
        pagination=pagination
    )

@admin_bp.route('/expedientes/descargar-zip')
@login_required
def descargar_expedientes_zip():

    ids = [int(i) for i in request.args.getlist('ids') if i.isdigit()]

    if not ids:
        abort(400, description='No se seleccionaron postulantes.')

    postulantes = Postulacion.query.filter(Postulacion.id.in_(ids)).all()


    usuarios_ya_procesados = set()
    postulantes_unicos = []

    for post in postulantes:
        if post.id_usuario not in usuarios_ya_procesados:
            usuarios_ya_procesados.add(post.id_usuario)
            postulantes_unicos.append(post)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for post in postulantes_unicos:
            usuario = User.query.get_or_404(post.id_usuario)
            personal = Personal.query.filter_by(id_usuario=post.id_usuario).first()
            vacante = Vacante.query.get(post.id_vacante)

            # Sin información personal no se puede armar la hoja de vida
            if personal is None or vacante is None:
                continue
            academica = Info_academica.query.filter_by(id_usuario=post.id_usuario).all()
            referencias = Referencias.query.filter_by(id_usuario=post.id_usuario).all()

            pdf_buffer = generar_pdf_expediente(
                personal=personal,
                vacante=vacante,
                post=post,
                academica=academica,
                referencias=referencias,
                usuario=usuario,
            )

            nombre_archivo = f"Hoja_de_vida_{personal.nombres}_{personal.apellidos}_{post.id}.pdf"
            zf.writestr(nombre_archivo, pdf_buffer.read())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='hojas_de_vida.zip',
        mimetype='application/zip',
    )

#### Gestion de envio de citaciones ########

def enviar_correo_citacion(email, nombres, fecha, hora, lugar, mensaje, link_confirmar, link_rechazar):
    return enviar_correo(
        email,
        'Has sido citado a una entrevista',
        "c_citacion.html",
        nombres=nombres,
        fecha=fecha,
        hora=hora,
        lugar=lugar,
        mensaje=mensaje,
        link_confirmar=link_confirmar,
        link_rechazar=link_rechazar,
    )


def _fecha_o_none(texto):
    try:
        return datetime.strptime(texto, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


@admin_bp.route("/citaciones")
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

    if vacante_id and vacante_id.isdigit():
        query = query.filter(Postulacion.id_vacante == int(vacante_id))

    fecha_desde_dt = _fecha_o_none(fecha_desde)
    if fecha_desde_dt:
        query = query.filter(Citaciones.fecha >= fecha_desde_dt)

    fecha_hasta_dt = _fecha_o_none(fecha_hasta)
    if fecha_hasta_dt:
        query = query.filter(Citaciones.fecha <= fecha_hasta_dt)

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

    page = request.args.get('page', 1, type=int)
    paginado = query.order_by(
        Citaciones.fecha.desc(), Citaciones.hora.desc(), Citaciones.id.desc()
    ).paginate(page=page, per_page=15, error_out=False)
    citaciones = paginado.items
    pagination = {
        'page': paginado.page,
        'pages': paginado.pages,
        'total': paginado.total,
        'has_prev': paginado.has_prev,
        'has_next': paginado.has_next,
        'prev_num': paginado.prev_num,
        'next_num': paginado.next_num,
    }

    return render_template(
        'admin/citaciones.html',
        citaciones=citaciones,
        vacantes=vacantes,
        q=q,
        vacante_seleccionada=vacante_id,
        estados_seleccionados=estados_seleccionados,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        pagination=pagination,
    )

@admin_bp.route('/vacantes/<int:id>/citar-seleccionados', methods=['POST'])
@login_required
def citar_seleccionados(id):
    datos_raw = request.form.get('postulaciones_seleccionadas')

    if not datos_raw:
        flash('No seleccionaste ningún postulante.', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))

    try:
        datos = json.loads(datos_raw)
    except ValueError:
        datos = None
    if not isinstance(datos, dict):
        flash('Los datos de la citación no son válidos.', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))

    ids = datos.get('ids', [])
    fecha_str = datos.get('fecha')
    hora_str = datos.get('hora')
    lugar = datos.get('lugar') or 'Por confirmar'
    mensaje = datos.get('mensaje') or ''
 
    if not ids or not fecha_str or not hora_str:
        flash('Faltan datos para citar (fecha, hora o postulantes).', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))
 
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
    except ValueError:
        flash('La fecha o la hora tienen un formato inválido.', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))

    if datetime.combine(fecha, hora) <= datetime.now():
        flash('La citación debe ser en una fecha y hora futuras.', 'error')
        return redirect(url_for('admin.listar_postulantes', id=id))

    # Solo postulaciones de esta vacante, aunque el formulario envíe otros ids
    postulaciones = Postulacion.query.filter(
        Postulacion.id.in_(ids),
        Postulacion.id_vacante == id,
    ).all()

    enviados = 0
    fallidos = 0
 
    for post in postulaciones:
        candidato = User.query.get(post.id_usuario)
 
        if not candidato or not candidato.correo:
            fallidos += 1
            continue
 
        token = secrets.token_urlsafe(32)
 
        nueva_citacion = Citaciones(
            id_postulacion=post.id,
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            mensaje=mensaje,
            estado='pendiente',
            token=token,
            fecha_envio=datetime.now()
        )
 
        link_confirmacion = url_for(
            'usuario.responder_citacion',
            token=token,
            respuesta='confirmar',
            _external=True
        )
        link_rechazo = url_for(
            'usuario.responder_citacion',
            token=token,
            respuesta='rechazar',
            _external=True
        )
 
        exito = enviar_correo_citacion(
            email=candidato.correo,
            nombres=candidato.nombres,
            fecha=fecha_str,
            hora=hora_str,
            lugar=lugar,
            mensaje=mensaje,
            link_confirmar=link_confirmacion,
            link_rechazar=link_rechazo,
        )
 
        if exito:
            # Solo se guarda la citación si el candidato recibió el correo
            db.session.add(nueva_citacion)
            if post.estado != 'entrevista':
                _cambiar_estado(post, 'entrevista')
            registrar_evento(
                post.id,
                "Citado a entrevista",
                f"{fecha.strftime('%d/%m/%Y')} a las {hora_str} · {lugar}",
            )
            enviados += 1
        else:
            fallidos += 1
 
    db.session.commit()
 
    if fallidos == 0:
        flash(f'Se citó a {enviados} postulante(s) correctamente.', 'success')
    else:
        flash(f'Se citó a {enviados} postulante(s). {fallidos} correo(s) no se pudieron enviar.', 'warning')
 
    return redirect(url_for('admin.listar_postulantes', id=id))



@admin_bp.route("/citaciones/<int:id>/reprogramar", methods=["POST"])
@login_required
def reprogramar_citacion(id):

    if session.get("rol") != "admin":
        return "No tienes permiso para realizar esta acción", 403

    citacion = Citaciones.query.get_or_404(id)

    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    lugar = request.form.get("lugar") or citacion.lugar
    mensaje = request.form.get("mensaje") or ""

    if not fecha or not hora:
        flash("Debes indicar la nueva fecha y hora.", "error")
        return redirect(url_for("admin.listar_citaciones"))

    postulacion = Postulacion.query.get_or_404(
        citacion.id_postulacion
    )

    personal = Personal.query.filter_by(
        id_usuario=postulacion.id_usuario
    ).first()
    usuario = User.query.get(postulacion.id_usuario)

    if not personal or not usuario or not usuario.correo:
        flash("No se encontró la información de contacto de la cuenta del candidato.", "error")
        return redirect(url_for("admin.listar_citaciones"))

    try:
        nueva_fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        nueva_hora = datetime.strptime(hora, "%H:%M").time()
    except ValueError:
        flash("La fecha o la hora tienen un formato inválido.", "error")
        return redirect(url_for("admin.listar_citaciones"))

    if datetime.combine(nueva_fecha, nueva_hora) <= datetime.now():
        flash("La nueva citación debe ser en una fecha y hora futuras.", "error")
        return redirect(url_for("admin.listar_citaciones"))

    citacion.fecha = nueva_fecha
    citacion.hora = nueva_hora

    citacion.lugar = lugar
    citacion.mensaje = mensaje

    # Reiniciar la respuesta anterior
    citacion.respuesta = None
    citacion.estado = "pendiente"
    citacion.fecha_respuesta = None

    registrar_evento(
        postulacion.id,
        "Entrevista reprogramada",
        f"{nueva_fecha.strftime('%d/%m/%Y')} a las {hora} · {lugar}",
    )
    db.session.commit()

    # Enlaces para responder a la nueva citación
    link_confirmar = url_for(
        "usuario.responder_citacion",
        token=citacion.token,
        respuesta="confirmar",
        _external=True
    )

    link_rechazar = url_for(
        "usuario.responder_citacion",
        token=citacion.token,
        respuesta="rechazar",
        _external=True
    )

    enviar_correo_citacion(
        email=usuario.correo,
        nombres=personal.nombres,
        fecha=fecha,
        hora=hora,
        lugar=lugar,
        mensaje=f"Tu entrevista ha sido reprogramada. {mensaje}",
        link_confirmar=link_confirmar,
        link_rechazar=link_rechazar
    )

    flash(
        "Citación reprogramada y correo enviado correctamente.",
        "success"
    )

    return redirect(
        url_for("admin.listar_citaciones")
    )

def enviar_correo_rechazo(email, nombres, vacante):
    return enviar_correo(
        email,
        'Resultado de tu postulación',
        "c_rechazo.html",
        nombres=nombres,
        vacante=vacante,
    )


@admin_bp.route("/postulacion/<int:id>/enviar-rechazo", methods=["POST"])
@login_required
def enviar_rechazo(id):
    if session.get("rol") != "admin":
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.", 403)

    postulacion = Postulacion.query.get_or_404(id)

    if postulacion.estado != 'rechazado':
        flash('Solo se puede enviar este correo a postulaciones en estado "Rechazado".', 'error')
        return redirect(url_for('admin.ver_expediente', id=id))

    candidato = User.query.get(postulacion.id_usuario)
    vacante = Vacante.query.get(postulacion.id_vacante)

    if not candidato or not candidato.correo or not vacante:
        flash('El candidato no tiene correo registrado.', 'warning')
        return redirect(url_for('admin.ver_expediente', id=id))

    enviado = enviar_correo_rechazo(
        email=candidato.correo,
        nombres=candidato.nombres,
        vacante=vacante.titulo,
    )

    if enviado:
        postulacion.fecha_correo_rechazo = datetime.now()
        registrar_evento(postulacion.id, "Se envió el correo de rechazo al candidato")
        db.session.commit()
        flash('Correo de rechazo enviado al candidato.', 'success')
    else:
        flash('No se pudo enviar el correo. Intenta de nuevo.', 'error')

    return redirect(url_for('admin.ver_expediente', id=id))