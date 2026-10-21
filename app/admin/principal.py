
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
from app.models.experiencia import Experiencia
from app.models.citacion import ESTADO_CANCELADA, Citaciones
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
from app.utils.correo import enviar_correo, url_externa
from app.utils.requisitos import cumple_requisitos, detalle_requisitos
from app.utils.formato import fecha_con_dia, hora_12
from app.utils.archivos import ruta_absoluta
from app.utils.historial import historial_de, registrar_evento
from app.constantes import ESTADOS_POSTULACION, MENSAJE_DESDE_STOCK, MENSAJES_CAMBIO_ESTADO
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
        Citaciones.vigente(),
        or_(Citaciones.respuesta.is_(None), Citaciones.respuesta != 'rechazada'),
    )

    return [
        {
            "titulo": "Postulaciones sin revisar",
            "detalle": f"En estado Postulado hace más de {DIAS_SIN_REVISAR} días",
            "cantidad": Postulacion.query.filter(
                Postulacion.estado == 'postulado',
                Postulacion.fecha_postulacion < hoy - timedelta(days=DIAS_SIN_REVISAR),
            ).count(),
            "url": url_for(
                'admin.listar_hoja_vida',
                estado='postulado',
                fecha_hasta=(hoy - timedelta(days=DIAS_SIN_REVISAR + 1)).isoformat(),
            ),
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
                Citaciones.vigente(), Citaciones.respuesta.is_(None), Citaciones.fecha >= hoy
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
    nivel = request.args.get("nivel", "").strip()
    postulaciones = request.args.get("postulaciones", "").strip()
    if postulaciones not in ("con", "sin"):
        postulaciones = ""
    estado = request.args.get("estado", "").strip()
    fecha_desde = request.args.get("fecha_publicacion_desde", "").strip()
    fecha_hasta = request.args.get("fecha_publicacion_hasta", "").strip()

    page = request.args.get("page", 1, type=int)
    per_page = 15
    # Accesos directos desde los pendientes del dashboard
    solo_vencidas = request.args.get("vencidas") == "1"
    solo_sin_funciones = request.args.get("sin_funciones") == "1"

    # Si las fechas llegan al revés se intercambian, en vez de no mostrar nada
    fechas_invertidas = bool(fecha_desde and fecha_hasta and fecha_desde > fecha_hasta)
    if fechas_invertidas:
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

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

    if nivel:
        query = query.filter(Vacante.nivel_academico == nivel)

    if estado:
        query = query.filter(Vacante.estado == estado)

    tiene_postulaciones = exists().where(Postulacion.id_vacante == Vacante.id)
    if postulaciones == "con":
        query = query.filter(tiene_postulaciones)
    elif postulaciones == "sin":
        query = query.filter(~tiene_postulaciones)

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
    areas_departamento = [v for v, _ in VacanteForm.area.kwargs["choices"] if v]
    # Mismos valores que guarda el formulario de vacantes
    niveles = [v for v, _ in VacanteForm.nivel_academico.kwargs["choices"] if v]

    # Filtros activos, para mostrarlos como etiquetas que se pueden quitar
    filtros_activos = []
    if q:
        filtros_activos.append(("q", f"“{q}”"))
    if area:
        filtros_activos.append(("area", area))
    if area_aplicacion:
        filtros_activos.append(("area_aplicacion", area_aplicacion))
    if nivel:
        filtros_activos.append(("nivel", nivel))
    if estado:
        filtros_activos.append(("estado", estado))
    if postulaciones:
        filtros_activos.append((
            "postulaciones",
            "Con postulaciones" if postulaciones == "con" else "Sin postulaciones",
        ))
    if solo_vencidas:
        filtros_activos.append(("vencidas", "Vencidas"))
    if _fecha_legible(fecha_desde):
        filtros_activos.append(
            ("fecha_publicacion_desde", "Desde " + _fecha_legible(fecha_desde))
        )
    if _fecha_legible(fecha_hasta):
        filtros_activos.append(
            ("fecha_publicacion_hasta", "Hasta " + _fecha_legible(fecha_hasta))
        )

    return render_template(
        "admin/listar_vacante.html",
        niveles=niveles,
        vacantes=vacantes,
        pagination=pagination,
        conteos=conteos,
        areas=areas_aplicacion,
        areas_departamento=areas_departamento,
        q=q,
        area_seleccionada=area,
        area_aplicacion_seleccionada=area_aplicacion,
        nivel_seleccionado=nivel,
        estado_seleccionado=estado,
        fecha_publicacion_desde_valor=fecha_desde,
        fecha_publicacion_hasta_valor=fecha_hasta,
        postulaciones_seleccionado=postulaciones,
        fechas_invertidas=fechas_invertidas,
        filtros_activos=filtros_activos,
        solo_vencidas=solo_vencidas,
        solo_sin_funciones=solo_sin_funciones,
    )


def _fecha_legible(texto):
    """'2026-10-21' -> '21/10/2026'; None si no es una fecha válida."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return None



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
        estados=ESTADOS_POSTULACION,
        sugerencias_stock=_sugerencias_stock(vacante),
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
    post = Postulacion.query.get_or_404(id)
    usuario = User.query.get_or_404(post.id_usuario)
    vacante = Vacante.query.get_or_404(post.id_vacante)
    uid = post.id_usuario

    # Puede faltar si el candidato no llenó Datos personales: la página igual se muestra
    personal = Personal.query.filter_by(id_usuario=uid).first()
    perfil_profesional = PerfilProfesional.query.filter_by(id_usuario=uid).first()
    funciones_perfil = FuncionArea.query.join(
        PerfilFuncion,
        PerfilFuncion.id_funcion == FuncionArea.id,
    ).filter(
        PerfilFuncion.id_usuario == uid,
    ).order_by(FuncionArea.nombre).all()
    academica = Info_academica.query.filter_by(id_usuario=uid).all()
    experiencia = Experiencia.query.filter_by(id_usuario=uid).order_by(Experiencia.fecha_ingreso.desc()).all()
    cursos = Cursos.query.filter_by(id_usuario=uid).order_by(Cursos.fecha_realizacion.desc()).all()
    referencias = Referencias.query.filter_by(id_usuario=uid).all()
    referencias_personales = ReferenciasPersonales.query.filter_by(id_usuario=uid).all()
    discapacidades = Discapacidades.query.filter_by(id_usuario=uid).all()
    documentos = OtrosDocumentos.query.filter_by(id_usuario=uid).all()

    funciones_vacante = funciones_de_vacante(vacante.id)
    coincidencia = resumen_coincidencia(
        funciones_vacante,
        {funcion.id for funcion in funciones_perfil},
    )

    # Última citación vigente (la de una reprogramación o una nueva cita)
    citacion = (
        Citaciones.query
        .filter(Citaciones.id_postulacion == post.id, Citaciones.vigente())
        .order_by(Citaciones.id.desc())
        .first()
    )

    # Otras postulaciones del mismo candidato, para saber si ya se le evaluó
    otras_postulaciones = (
        db.session.query(Postulacion, Vacante)
        .join(Vacante, Vacante.id == Postulacion.id_vacante)
        .filter(Postulacion.id_usuario == uid, Postulacion.id != post.id)
        .order_by(Postulacion.fecha_postulacion.desc())
        .all()
    )

    # Anterior / siguiente postulante de la misma vacante (orden de postulación)
    ids_vacante = [
        pid for (pid,) in
        db.session.query(Postulacion.id)
        .filter(Postulacion.id_vacante == vacante.id)
        .order_by(Postulacion.fecha_postulacion.desc(), Postulacion.id.desc())
    ]
    posicion = ids_vacante.index(post.id)
    navegacion = {
        "posicion": posicion + 1,
        "total": len(ids_vacante),
        "anterior": ids_vacante[posicion - 1] if posicion > 0 else None,
        "siguiente": ids_vacante[posicion + 1] if posicion + 1 < len(ids_vacante) else None,
    }

    ubicacion = ""
    if personal:
        ubicacion = ", ".join(
            parte for parte in (
                personal.direccion, personal.barrio,
                personal.municipio, personal.departamento,
            ) if parte and parte.strip()
        )

    return render_template(
        'admin/expediente.html',
        post=post,
        usuario=usuario,
        vacante=vacante,
        coincidencia=coincidencia,
        requisitos=detalle_requisitos(uid, vacante),
        historial=historial_de(post.id),
        personal=personal,
        ubicacion=ubicacion,
        perfil_profesional=perfil_profesional,
        funciones_perfil=funciones_perfil,
        academica=academica,
        experiencia=experiencia,
        experiencia_total=formatear_experiencia(obtener_experiencia_total(uid)),
        cursos=cursos,
        referencias=referencias,
        referencias_personales=referencias_personales,
        discapacidades=discapacidades,
        documentos=documentos,
        citacion=citacion,
        otras_postulaciones=otras_postulaciones,
        navegacion=navegacion,
        estados=ESTADOS_POSTULACION,
        hoy=date.today(),
    )

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

    if cambio_estado and request.form.get("notificar") == "1":
        if nuevo_estado == "rechazado":
            enviado = _notificar_rechazo(postulacion)
        elif nuevo_estado in MENSAJES_CAMBIO_ESTADO:
            enviado = _notificar_cambio_estado(postulacion, retiradas)
        else:
            enviado = None  # "Postulado" y "Retirada" no tienen correo
        if enviado:
            flash("Se avisó al candidato por correo.", "success")
        elif enviado is False:
            flash(
                "No se pudo enviar el correo al candidato. Puedes reenviarlo desde su expediente.",
                "warning",
            )
        db.session.commit()

    return redirect(url_for('admin.listar_postulantes', id=postulacion.id_vacante))

def _sugerencias_stock(vacante, limite=10):
    """Personas en stock de otras vacantes de la misma área de aplicación
    que todavía no están en esta vacante.

    [{"postulacion", "vacante", "usuario", "personal", "requisitos"}]
    """
    ya_en_vacante = db.session.query(Postulacion.id_usuario).filter(
        Postulacion.id_vacante == vacante.id
    )
    query = (
        db.session.query(Postulacion, Vacante, User, Personal)
        .join(Vacante, Vacante.id == Postulacion.id_vacante)
        .join(User, User.id == Postulacion.id_usuario)
        .outerjoin(Personal, Personal.id_usuario == Postulacion.id_usuario)
        .filter(
            Postulacion.estado == "stock",
            Postulacion.id_vacante != vacante.id,
            ~Postulacion.id_usuario.in_(ya_en_vacante),
        )
    )
    if (vacante.area_aplicacion or "").strip():
        query = query.filter(Vacante.area_aplicacion == vacante.area_aplicacion)

    sugerencias = []
    vistos = set()
    for postulacion, otra_vacante, usuario, personal in query.order_by(
        Postulacion.fecha_actualizacion.desc()
    ):
        # Una persona puede estar en stock en varias vacantes: se muestra una vez
        if usuario.id in vistos:
            continue
        vistos.add(usuario.id)
        sugerencias.append({
            "postulacion": postulacion,
            "vacante": otra_vacante,
            "usuario": usuario,
            "personal": personal,
            "requisitos": cumple_requisitos(usuario.id, vacante),
        })
        if len(sugerencias) >= limite:
            break
    return sugerencias


@admin_bp.route("/vacantes/<int:id>/agregar-desde-stock", methods=["POST"])
@login_required
def agregar_desde_stock(id):
    """Agrega a esta vacante a una persona que estaba en stock en otra."""
    vacante = Vacante.query.get_or_404(id)
    volver = redirect(url_for('admin.listar_postulantes', id=id))

    origen = db.session.get(Postulacion, request.form.get("postulacion_id", type=int))
    if origen is None or origen.estado != "stock":
        flash("Esa persona ya no está en stock.", "warning")
        return volver

    if Postulacion.query.filter_by(id_usuario=origen.id_usuario, id_vacante=id).first():
        flash("Esa persona ya está en esta vacante.", "warning")
        return volver

    vacante_origen = db.session.get(Vacante, origen.id_vacante)
    nueva = Postulacion(
        id_usuario=origen.id_usuario,
        id_vacante=id,
        estado="revision",
        fecha_postulacion=datetime.now(),
    )
    db.session.add(nueva)
    db.session.flush()  # para tener el id de la nueva postulación en el historial
    registrar_evento(
        nueva.id,
        "Agregado desde stock",
        f"Estaba en stock en la vacante \"{vacante_origen.titulo if vacante_origen else ''}\".",
    )
    registrar_evento(
        origen.id,
        "Se agregó a otra vacante desde stock",
        f"Vacante \"{vacante.titulo}\".",
    )
    db.session.commit()

    candidato = db.session.get(User, origen.id_usuario)
    enviado = bool(candidato and candidato.correo) and enviar_correo(
        candidato.correo,
        MENSAJE_DESDE_STOCK["asunto"],
        "correos/estado_postulacion.html",
        nombres=candidato.nombres,
        vacante=vacante.titulo,
        titulo=MENSAJE_DESDE_STOCK["titulo"],
        mensaje=MENSAJE_DESDE_STOCK["mensaje"],
        otras_retiradas=0,
    )
    if enviado:
        registrar_evento(nueva.id, "Se notificó al candidato por correo", MENSAJE_DESDE_STOCK["asunto"])
        db.session.commit()

    nombre = f"{candidato.nombres} {candidato.apellidos}" if candidato else "La persona"
    flash(
        f"{nombre} se agregó a la vacante en estado En revisión."
        + ("" if enviado else " No se pudo enviar el correo de aviso."),
        "success" if enviado else "warning",
    )
    return volver


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

    if accion not in ("revision", "rechazar", "stock") or not ids:
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

    if accion == "stock":
        # Gustaron pero no se eligieron: quedan guardados y se les avisa
        cambiadas = [
            p for p in postulaciones
            if p.estado not in ("contratado", "retirada", "rechazado", "stock")
        ]
        enviados = 0
        for postulacion in cambiadas:
            _cambiar_estado(postulacion, "stock")
            if _notificar_cambio_estado(postulacion):
                enviados += 1
        db.session.commit()
        mensaje = f"{len(cambiadas)} postulante(s) quedaron en stock; {enviados} correo(s) enviados."
        omitidas = len(postulaciones) - len(cambiadas)
        if omitidas:
            mensaje += f" {omitidas} ya estaban en stock, contratados, retirados o rechazados."
        flash(mensaje, "success" if enviados == len(cambiadas) else "warning")
        return volver

    # Rechazar y enviar correo
    cambiadas = [
        p for p in postulaciones
        if p.estado not in ("contratado", "retirada", "rechazado")
    ]
    enviados = 0
    for postulacion in cambiadas:
        _cambiar_estado(postulacion, "rechazado")
        if _notificar_rechazo(postulacion, vacante):
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


# Niveles del formulario académico (valor guardado, etiqueta) para el filtro
NIVELES_FILTRO_HV = [
    ('primaria', 'Primaria'), ('Bachillerato', 'Bachillerato'), ('tecnico', 'Técnico'),
    ('tecnologo', 'Tecnólogo'), ('universitario', 'Universitario'),
    ('especializacion', 'Especialización'), ('maestria', 'Maestría'), ('doctorado', 'Doctorado'),
]


def _consulta_hojas_de_vida(args):
    """Postulaciones con los filtros de la página de hojas de vida.

    La comparten el listado y la descarga en ZIP, para que "descargar todo"
    baje exactamente lo que se está viendo. Devuelve (query, filtros).
    """
    filtros = {
        'vacante_id': args.get('vacante_id', '').strip(),
        'estado': args.get('estado', '').strip(),
        'q': args.get('q', '').strip(),
        'fecha_desde': args.get('fecha_desde', '').strip(),
        'fecha_hasta': args.get('fecha_hasta', '').strip(),
        'nivel_academico': args.get('nivel_academico', '').strip(),
        'completitud': args.get('completitud', '').strip(),
        'fechas_invertidas': False,
    }
    if filtros['estado'] not in ESTADOS_POSTULACION:
        filtros['estado'] = ''
    if filtros['nivel_academico'] not in dict(NIVELES_FILTRO_HV):
        filtros['nivel_academico'] = ''
    if filtros['completitud'] not in ('completo', 'incompleto'):
        filtros['completitud'] = ''

    desde = _fecha_o_none(filtros['fecha_desde'])
    hasta = _fecha_o_none(filtros['fecha_hasta'])
    if desde and hasta and desde > hasta:
        desde, hasta = hasta, desde
        filtros['fechas_invertidas'] = True
    filtros['fecha_desde'] = desde.isoformat() if desde else ''
    filtros['fecha_hasta'] = hasta.isoformat() if hasta else ''

    # outerjoin: también aparecen quienes no han llenado Datos personales
    query = (
        db.session.query(Postulacion)
        .join(Vacante, Vacante.id == Postulacion.id_vacante)
        .join(User, User.id == Postulacion.id_usuario)
        .outerjoin(Personal, Personal.id_usuario == Postulacion.id_usuario)
    )

    if filtros['vacante_id'].isdigit():
        query = query.filter(Postulacion.id_vacante == int(filtros['vacante_id']))

    if filtros['estado']:
        query = query.filter(Postulacion.estado == filtros['estado'])

    if filtros['q']:
        busqueda = f"%{filtros['q']}%"
        query = query.filter(or_(
            Personal.nombres.ilike(busqueda),
            Personal.apellidos.ilike(busqueda),
            func.concat(Personal.nombres, ' ', Personal.apellidos).ilike(busqueda),
            Personal.num_doc.ilike(busqueda),
            User.nombres.ilike(busqueda),
            User.apellidos.ilike(busqueda),
            User.correo.ilike(busqueda),
        ))

    if desde:
        query = query.filter(Postulacion.fecha_postulacion >= datetime.combine(desde, datetime.min.time()))
    if hasta:
        query = query.filter(
            Postulacion.fecha_postulacion < datetime.combine(hasta + timedelta(days=1), datetime.min.time())
        )

    if filtros['nivel_academico']:
        query = query.filter(Postulacion.id_usuario.in_(
            db.session.query(Info_academica.id_usuario)
            .filter(Info_academica.nivel == filtros['nivel_academico'])
        ))

    query = query.order_by(Postulacion.fecha_postulacion.desc(), Postulacion.id.desc())
    return query, filtros


def _filtrar_por_completitud(postulaciones, completitud):
    """Filtra en Python (la completitud no se puede calcular en SQL).

    Calcula una sola vez por candidato aunque tenga varias postulaciones.
    """
    cache = {}
    resultado = []
    for post in postulaciones:
        if post.id_usuario not in cache:
            cache[post.id_usuario] = calcular_completitud_perfil(post.id_usuario)
        completo = cache[post.id_usuario]['porcentaje'] == 100
        if completo == (completitud == 'completo'):
            post.completitud = cache[post.id_usuario]
            resultado.append(post)
    return resultado


@admin_bp.route('/hoja-de-vida')
@login_required
def listar_hoja_vida():
    query, filtros = _consulta_hojas_de_vida(request.args)

    page = request.args.get('page', 1, type=int)
    per_page = 15

    if filtros['completitud']:
        todos = _filtrar_por_completitud(query.all(), filtros['completitud'])
        total = len(todos)
        paginas = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, paginas))   # una página fuera de rango va a la última
        postulantes = todos[(page - 1) * per_page: page * per_page]
    else:
        total = query.order_by(None).count()
        paginas = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, paginas))
        postulantes = query.offset((page - 1) * per_page).limit(per_page).all()

    pagination = {
        'page': page,
        'pages': paginas,
        'total': total,
        'has_prev': page > 1,
        'has_next': page < paginas,
        'prev_num': page - 1,
        'next_num': page + 1,
    }

    # Datos de cada fila en pocas consultas (antes eran ~15 por fila)
    ids_usuarios = {post.id_usuario for post in postulantes}
    ids_vacantes = {post.id_vacante for post in postulantes}
    personales = {
        personal.id_usuario: personal
        for personal in Personal.query.filter(Personal.id_usuario.in_(ids_usuarios))
    } if ids_usuarios else {}
    usuarios = {u.id: u for u in User.query.filter(User.id.in_(ids_usuarios))} if ids_usuarios else {}
    vacantes_fila = {v.id: v for v in Vacante.query.filter(Vacante.id.in_(ids_vacantes))} if ids_vacantes else {}
    completitudes = {}
    niveles = {}
    for post in postulantes:
        post.personal = personales.get(post.id_usuario)
        post.usuario = usuarios.get(post.id_usuario)
        post.vacante = vacantes_fila.get(post.id_vacante)
        if not getattr(post, 'completitud', None):
            if post.id_usuario not in completitudes:
                completitudes[post.id_usuario] = calcular_completitud_perfil(post.id_usuario)
            post.completitud = completitudes[post.id_usuario]
        if post.id_usuario not in niveles:
            niveles[post.id_usuario] = obtener_nivel_mas_alto(post.id_usuario)
        post.nivel_mas_alto = niveles[post.id_usuario]

    vacantes = Vacante.query.order_by(Vacante.titulo.asc()).all()

    # Filtros activos, para mostrarlos como etiquetas que se pueden quitar
    filtros_activos = []
    if filtros['q']:
        filtros_activos.append(('q', f"“{filtros['q']}”"))
    if filtros['vacante_id'].isdigit():
        vacante = next((v for v in vacantes if v.id == int(filtros['vacante_id'])), None)
        filtros_activos.append(('vacante_id', vacante.titulo if vacante else 'Vacante'))
    if filtros['estado']:
        filtros_activos.append(('estado', ESTADOS_POSTULACION[filtros['estado']]))
    if filtros['nivel_academico']:
        filtros_activos.append(('nivel_academico', dict(NIVELES_FILTRO_HV)[filtros['nivel_academico']]))
    if filtros['completitud']:
        filtros_activos.append((
            'completitud', 'Completos' if filtros['completitud'] == 'completo' else 'Incompletos',
        ))
    if filtros['fecha_desde']:
        filtros_activos.append(('fecha_desde', 'Desde ' + _fecha_legible(filtros['fecha_desde'])))
    if filtros['fecha_hasta']:
        filtros_activos.append(('fecha_hasta', 'Hasta ' + _fecha_legible(filtros['fecha_hasta'])))

    return render_template(
        'listar_hojas_de_vida.html',
        vacantes=vacantes,
        postulantes=postulantes,
        estados=ESTADOS_POSTULACION,
        niveles=NIVELES_FILTRO_HV,
        vacante_seleccionada=filtros['vacante_id'],
        estado_seleccionado=filtros['estado'],
        q=filtros['q'],
        fecha_desde=filtros['fecha_desde'],
        fecha_hasta=filtros['fecha_hasta'],
        fechas_invertidas=filtros['fechas_invertidas'],
        nivel_academico_seleccionado=filtros['nivel_academico'],
        completitud_seleccionada=filtros['completitud'],
        filtros_activos=filtros_activos,
        pagination=pagination,
    )

# Cada hoja de vida es un PDF generado en el momento: se limita el tamaño del ZIP
MAX_ZIP_HOJAS_DE_VIDA = 200


@admin_bp.route('/expedientes/descargar-zip')
@login_required
def descargar_expedientes_zip():

    ids = [int(i) for i in request.args.getlist('ids') if i.isdigit()]
    volver = request.referrer or url_for('admin.listar_hoja_vida')

    if ids:
        postulantes = Postulacion.query.filter(Postulacion.id.in_(ids)).all()
    elif request.args.get('todos') == '1':
        # "Descargar todos": los mismos que muestra el listado con sus filtros
        query, filtros = _consulta_hojas_de_vida(request.args)
        postulantes = query.all()
        if filtros['completitud']:
            postulantes = _filtrar_por_completitud(postulantes, filtros['completitud'])
        if len(postulantes) > MAX_ZIP_HOJAS_DE_VIDA:
            flash(
                f'Son {len(postulantes)} hojas de vida; el máximo por descarga es '
                f'{MAX_ZIP_HOJAS_DE_VIDA}. Filtra un poco más o selecciónalas por páginas.',
                'warning',
            )
            return redirect(volver)
    else:
        flash('No seleccionaste ningún postulante.', 'warning')
        return redirect(volver)


    usuarios_ya_procesados = set()
    postulantes_unicos = []

    for post in postulantes:
        if post.id_usuario not in usuarios_ya_procesados:
            usuarios_ya_procesados.add(post.id_usuario)
            postulantes_unicos.append(post)

    zip_buffer = io.BytesIO()
    incluidos = 0
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
            incluidos += 1

    if not incluidos:
        flash('Ninguno de los candidatos tiene datos personales; no hay hojas de vida para descargar.', 'warning')
        return redirect(volver)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='hojas_de_vida.zip',
        mimetype='application/zip',
    )

#### Gestion de envio de citaciones ########

def enviar_correo_citacion(email, nombres, fecha, hora, lugar, mensaje, link_confirmar,
                           link_rechazar, vacante="", reprogramada=False):
    """fecha y hora son date/time: en el correo salen como 'viernes 24 de
    octubre de 2026' y '9:30 a. m.'."""
    asunto = (
        'Tu entrevista fue reprogramada' if reprogramada
        else 'Has sido citado a una entrevista'
    )
    return enviar_correo(
        email,
        asunto,
        "c_citacion.html",
        nombres=nombres,
        vacante=vacante,
        reprogramada=reprogramada,
        fecha=fecha_con_dia(fecha),
        hora=hora_12(hora),
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


# Estado de la citación que se elige en el filtro -> condición SQL
ESTADOS_CITACION = {
    "sin_responder": "Sin responder",
    "confirmada": "Confirmada",
    "rechazada": "No asistirá",
    "cancelada": "Cancelada",
}


def _condicion_estado_citacion(estado):
    if estado == "cancelada":
        return Citaciones.estado == ESTADO_CANCELADA
    condicion = {
        "sin_responder": Citaciones.respuesta.is_(None),
        "confirmada": Citaciones.respuesta == "confirmada",
        "rechazada": Citaciones.respuesta == "rechazada",
    }[estado]
    return db.and_(Citaciones.vigente(), condicion)


@admin_bp.route("/citaciones")
@login_required
def listar_citaciones():

    q = request.args.get('q', '').strip()
    vacante_id = request.args.get('vacante_id', '').strip()
    # Se admite más de un estado (?estado=a&estado=b), como llegan desde el dashboard
    estados_seleccionados = [
        e for e in request.args.getlist('estado') if e in ESTADOS_CITACION
    ]
    cuando = request.args.get('cuando', '').strip()
    if cuando not in ('proximas', 'pasadas'):
        cuando = ''
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    fecha_desde_dt = _fecha_o_none(fecha_desde)
    fecha_hasta_dt = _fecha_o_none(fecha_hasta)
    fechas_invertidas = bool(fecha_desde_dt and fecha_hasta_dt and fecha_desde_dt > fecha_hasta_dt)
    if fechas_invertidas:
        fecha_desde_dt, fecha_hasta_dt = fecha_hasta_dt, fecha_desde_dt
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    # Solo vacantes que tienen citaciones, para no llenar el selector
    vacantes = (
        Vacante.query
        .filter(Vacante.id.in_(
            db.session.query(Postulacion.id_vacante)
            .join(Citaciones, Citaciones.id_postulacion == Postulacion.id)
        ))
        .order_by(Vacante.titulo.asc())
        .all()
    )

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
        query = query.filter(or_(
            User.nombres.ilike(busqueda),
            User.apellidos.ilike(busqueda),
            User.correo.ilike(busqueda),
            func.concat(User.nombres, ' ', User.apellidos).ilike(busqueda),
        ))

    if vacante_id.isdigit():
        query = query.filter(Postulacion.id_vacante == int(vacante_id))

    hoy = date.today()
    if cuando == 'proximas':
        query = query.filter(Citaciones.fecha >= hoy)
    elif cuando == 'pasadas':
        query = query.filter(Citaciones.fecha < hoy)

    if fecha_desde_dt:
        query = query.filter(Citaciones.fecha >= fecha_desde_dt)
    if fecha_hasta_dt:
        query = query.filter(Citaciones.fecha <= fecha_hasta_dt)

    if estados_seleccionados:
        query = query.filter(or_(*[
            _condicion_estado_citacion(e) for e in estados_seleccionados
        ]))

    # Las próximas se leen como agenda (la más cercana primero)
    if cuando == 'proximas':
        orden = (Citaciones.fecha.asc(), Citaciones.hora.asc(), Citaciones.id.asc())
    else:
        orden = (Citaciones.fecha.desc(), Citaciones.hora.desc(), Citaciones.id.desc())

    page = request.args.get('page', 1, type=int)
    paginado = query.order_by(*orden).paginate(page=page, per_page=15, error_out=False)
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

    # Para el detalle de cada citación: teléfono del candidato y todas las
    # citaciones de su postulación (reprogramadas o reemplazadas)
    ids_usuarios = {candidato.id for _, _, candidato, _ in citaciones}
    ids_postulaciones = {postulacion.id for _, postulacion, _, _ in citaciones}
    telefonos = {}
    historial = {}
    if citaciones:
        telefonos = {
            personal.id_usuario: personal.num_cel
            for personal in Personal.query.filter(Personal.id_usuario.in_(ids_usuarios))
        }
        for anterior in (
            Citaciones.query
            .filter(Citaciones.id_postulacion.in_(ids_postulaciones))
            .order_by(Citaciones.id.desc())
        ):
            historial.setdefault(anterior.id_postulacion, []).append(anterior)

    # Filtros activos, para mostrarlos como etiquetas que se pueden quitar
    filtros_activos = []
    if q:
        filtros_activos.append(('q', None, f"“{q}”"))
    if vacante_id.isdigit():
        vacante = next((v for v in vacantes if v.id == int(vacante_id)), None)
        filtros_activos.append(('vacante_id', None, vacante.titulo if vacante else f"Vacante {vacante_id}"))
    for estado in estados_seleccionados:
        filtros_activos.append(('estado', estado, ESTADOS_CITACION[estado]))
    if cuando:
        filtros_activos.append(('cuando', None, 'Próximas' if cuando == 'proximas' else 'Pasadas'))
    if fecha_desde_dt:
        filtros_activos.append(('fecha_desde', None, 'Desde ' + fecha_desde_dt.strftime('%d/%m/%Y')))
    if fecha_hasta_dt:
        filtros_activos.append(('fecha_hasta', None, 'Hasta ' + fecha_hasta_dt.strftime('%d/%m/%Y')))

    return render_template(
        'admin/citaciones.html',
        citaciones=citaciones,
        vacantes=vacantes,
        estados=ESTADOS_CITACION,
        q=q,
        vacante_seleccionada=vacante_id,
        estados_seleccionados=estados_seleccionados,
        cuando=cuando,
        fecha_desde=fecha_desde_dt.isoformat() if fecha_desde_dt else '',
        fecha_hasta=fecha_hasta_dt.isoformat() if fecha_hasta_dt else '',
        fechas_invertidas=fechas_invertidas,
        filtros_activos=filtros_activos,
        telefonos=telefonos,
        historial=historial,
        hoy=hoy,
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
    vacante = db.session.get(Vacante, id)

    enviados = 0
    fallidos = 0
    omitidos = 0

    for post in postulaciones:
        # Un proceso cerrado no se cita a entrevista
        if post.estado in ('contratado', 'rechazado', 'retirada'):
            omitidos += 1
            continue

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
 
        link_confirmacion = url_externa(
            'usuario.responder_citacion', token=token, respuesta='confirmar'
        )
        link_rechazo = url_externa(
            'usuario.responder_citacion', token=token, respuesta='rechazar'
        )

        exito = enviar_correo_citacion(
            email=candidato.correo,
            nombres=candidato.nombres,
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            mensaje=mensaje,
            link_confirmar=link_confirmacion,
            link_rechazar=link_rechazo,
            vacante=vacante.titulo if vacante else "",
        )

        if exito:
            # La citación anterior queda cancelada: sus enlaces dejan de servir
            # y no aparece dos veces en el listado
            Citaciones.query.filter(
                Citaciones.id_postulacion == post.id,
                Citaciones.vigente(),
            ).update({"estado": ESTADO_CANCELADA}, synchronize_session=False)
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
 
    partes = [f'Se citó a {enviados} postulante(s).']
    if fallidos:
        partes.append(f'{fallidos} correo(s) no se pudieron enviar.')
    if omitidos:
        partes.append(f'{omitidos} se omitieron porque su proceso ya terminó.')
    flash(' '.join(partes), 'success' if not (fallidos or omitidos) else 'warning')

    volver = request.form.get('volver') or ''
    if volver.startswith('/'):
        return redirect(volver)
    return redirect(url_for('admin.listar_postulantes', id=id))



@admin_bp.route("/citaciones/<int:id>/reprogramar", methods=["POST"])
@login_required
def reprogramar_citacion(id):
    citacion = Citaciones.query.get_or_404(id)
    volver = request.form.get("volver") or url_for("admin.listar_citaciones")
    if not volver.startswith("/"):
        volver = url_for("admin.listar_citaciones")

    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    lugar = (request.form.get("lugar") or "").strip() or citacion.lugar
    mensaje = (request.form.get("mensaje") or "").strip()

    if citacion.cancelada:
        flash("Esta citación fue cancelada; cita de nuevo desde la lista de postulantes.", "error")
        return redirect(volver)

    if not fecha or not hora:
        flash("Debes indicar la nueva fecha y hora.", "error")
        return redirect(volver)

    postulacion = Postulacion.query.get_or_404(citacion.id_postulacion)
    if postulacion.estado in ('contratado', 'rechazado', 'retirada'):
        flash("El proceso de este candidato ya terminó; no se puede reprogramar.", "error")
        return redirect(volver)

    usuario = User.query.get(postulacion.id_usuario)
    if not usuario or not usuario.correo:
        flash("El candidato no tiene un correo registrado.", "error")
        return redirect(volver)

    try:
        nueva_fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        nueva_hora = datetime.strptime(hora, "%H:%M").time()
    except ValueError:
        flash("La fecha o la hora tienen un formato inválido.", "error")
        return redirect(volver)

    if datetime.combine(nueva_fecha, nueva_hora) <= datetime.now():
        flash("La nueva citación debe ser en una fecha y hora futuras.", "error")
        return redirect(volver)

    vacante = db.session.get(Vacante, postulacion.id_vacante)

    # Primero el correo: si no sale, la citación queda como estaba
    enviado = enviar_correo_citacion(
        email=usuario.correo,
        nombres=usuario.nombres,
        fecha=nueva_fecha,
        hora=nueva_hora,
        lugar=lugar,
        mensaje=mensaje,
        link_confirmar=url_externa(
            "usuario.responder_citacion", token=citacion.token, respuesta="confirmar"
        ),
        link_rechazar=url_externa(
            "usuario.responder_citacion", token=citacion.token, respuesta="rechazar"
        ),
        vacante=vacante.titulo if vacante else "",
        reprogramada=True,
    )
    if not enviado:
        flash("No se pudo enviar el correo al candidato; la citación no se cambió.", "error")
        return redirect(volver)

    citacion.fecha = nueva_fecha
    citacion.hora = nueva_hora
    citacion.lugar = lugar
    citacion.mensaje = mensaje
    citacion.fecha_envio = datetime.now()

    # El candidato debe responder de nuevo
    citacion.respuesta = None
    citacion.estado = "pendiente"
    citacion.fecha_respuesta = None

    registrar_evento(
        postulacion.id,
        "Entrevista reprogramada",
        f"{nueva_fecha.strftime('%d/%m/%Y')} a las {nueva_hora.strftime('%H:%M')} · {lugar}",
    )
    db.session.commit()

    flash("Citación reprogramada y correo enviado al candidato.", "success")
    return redirect(volver)

def enviar_correo_rechazo(email, nombres, vacante):
    return enviar_correo(
        email,
        'Resultado de tu postulación',
        "c_rechazo.html",
        nombres=nombres,
        vacante=vacante,
    )


def _notificar_rechazo(postulacion, vacante=None):
    """Envía el correo de rechazo y lo registra (no hace commit).

    Lo usan el cambio de estado del expediente, la acción masiva
    "Rechazar y enviar correo" y el reenvío. Devuelve True si se envió.
    """
    candidato = db.session.get(User, postulacion.id_usuario)
    vacante = vacante or db.session.get(Vacante, postulacion.id_vacante)
    if not candidato or not candidato.correo or not vacante:
        return False
    if not enviar_correo_rechazo(
        email=candidato.correo,
        nombres=candidato.nombres,
        vacante=vacante.titulo,
    ):
        return False
    postulacion.fecha_correo_rechazo = datetime.now()
    registrar_evento(postulacion.id, "Se envió el correo de rechazo al candidato")
    return True


@admin_bp.route("/postulacion/<int:id>/enviar-rechazo", methods=["POST"])
@login_required
def enviar_rechazo(id):
    if session.get("rol") != "admin":
        return ("Hola, no deberias estar aqui, debe haber ocurrido un error.", 403)

    postulacion = Postulacion.query.get_or_404(id)

    if postulacion.estado != 'rechazado':
        flash('Solo se puede enviar este correo a postulaciones en estado "Rechazado".', 'error')
        return redirect(url_for('admin.ver_expediente', id=id))

    if _notificar_rechazo(postulacion):
        db.session.commit()
        flash('Correo de rechazo enviado al candidato.', 'success')
    else:
        flash('No se pudo enviar el correo. Revisa que el candidato tenga correo e intenta de nuevo.', 'error')

    return redirect(url_for('admin.ver_expediente', id=id))