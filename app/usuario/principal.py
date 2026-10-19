
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    jsonify,
)
import json

from typing import Optional
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Response

from flask_login import current_user, login_required
from flask_wtf import FlaskForm
import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import date, datetime
from app.extensions import db
from app.models.user import User
from app.models.personal import Personal
from app.forms.personal import InfoPersonalForm
from app.forms.academica import InforAcademicaForm
from app.models.academica import Info_academica
from app.forms.experiencia import experienciaForm
from app.models.experiencia import Experiencia
from app.models.funcion_area import FuncionArea
from app.models.perfil_funcion import PerfilFuncion
from app.models.perfil_profesional import PerfilProfesional
from app.models.cursos import Cursos
from app.forms.cursos import CursoForm
from app.forms.referencias import referenciasForm
from app.models.referencias import Referencias
from app.models.referencias_personales import ReferenciasPersonales
from app.forms.referencias_personales import referenciasPersonalesForm
from app.forms.discapacidades import discapacidadForm
from app.models.discapacidades import Discapacidades
from app.constantes import (
    DISCAPACIDAD_CATEGORIAS,
    DISCAPACIDAD_CATEGORIAS_LEGADAS,
)
from app.forms.docs import documentoForm
from app.forms.docs import documentoItemForm
from app.models.docs import OtrosDocumentos
from app.models.paso_omitido import PasoOmitido
from app.forms.vacante import VacanteForm
from app.models.vacante import Vacante
from app.models.postulacion import Postulacion
from app.models.citacion import Citaciones
from app.utils.perfil import (
    calcular_completitud_perfil,
    formatear_experiencia,
    obtener_experiencia_total,
)
from app.utils.requisitos import cumple_requisitos
from app.forms.validaciones import (
    a_fecha,
    fila_vacia,
    validar_academica,
    validar_cursos,
    validar_discapacidades,
    validar_experiencia,
    validar_referencias,
    validar_referencias_personales,
    rangos_se_cruzan,
)
from .constantes import (
    PASOS_seguimiento,
    NOMBRES_PASO,
    DESCRIPCIONES_PASO,
    REGLAS_PASO,
    TOTAL_PASOS,
)



from . import usuario_bp


def _declaracion_marcada(paso):
    campo = REGLAS_PASO[paso].get("campo_declaracion")
    return bool(campo and request.form.get(campo) == "1")


def _guardar_declaracion_paso(paso):
    declaracion = PasoOmitido.query.filter_by(
        id_usuario=current_user.id,
        paso=paso,
    ).first()
    if declaracion is None:
        db.session.add(
            PasoOmitido(
                id_usuario=current_user.id,
                paso=paso,
                fecha_declaracion=datetime.now(),
            )
        )


def _limpiar_declaracion_paso(paso):
    declaracion = PasoOmitido.query.filter_by(
        id_usuario=current_user.id,
        paso=paso,
    ).first()
    if declaracion is not None:
        db.session.delete(declaracion)


def _tiene_declaracion_paso(paso):
    return PasoOmitido.query.filter_by(
        id_usuario=current_user.id,
        paso=paso,
    ).first() is not None


def _minimo_registros_cumplido(paso, entradas, campos, registros_guardados):
    minimo = REGLAS_PASO[paso].get("minimo", 0)
    registros_por_id = {registro.id: registro for registro in registros_guardados}
    entradas_por_id = {}

    for entry in entradas:
        try:
            registro_id = int(entry.registro_id.data)
        except (TypeError, ValueError):
            continue
        if registro_id in registros_por_id:
            entradas_por_id[registro_id] = entry

    cantidad = 0
    for registro_id in registros_por_id:
        entry = entradas_por_id.get(registro_id)
        if entry is None or (
            entry.eliminar.data != "1" and not fila_vacia(entry, campos)
        ):
            cantidad += 1

    for entry in entradas:
        if entry.eliminar.data == "1" or fila_vacia(entry, campos):
            continue
        try:
            registro_id = int(entry.registro_id.data)
        except (TypeError, ValueError):
            registro_id = None
        if registro_id not in registros_por_id:
            cantidad += 1

    return cantidad >= minimo


def _hay_registro_valido_enviado(entradas, campos):
    return any(
        entry.eliminar.data != "1" and not fila_vacia(entry, campos)
        for entry in entradas
    )


def _asociar_errores_a_campos(entry, errores, paso):
    campos_por_mensaje = {
        "academica": (
            ("nivel", "nivel"),
            ("estado", "estado"),
            ("título", "titulo"),
            ("institución", "institucion"),
        ),
        "cursos": (
            ("nombre", "nombre"),
            ("institución", "institucion"),
        ),
        "referencias": (
            ("apellidos", "apellidos"),
            ("nombre", "nombres"),
            ("empresa", "empresa"),
            ("autorización", "autoriza"),
        ),
        "referencias_personales": (
            ("apellidos", "apellidos"),
            ("nombre", "nombres"),
            ("parentesco", "parentesco"),
            ("teléfono", "telefono"),
        ),
        "discapacidades": (
            ("categoría", "categoria"),
        ),
    }
    errores_sin_campo = []

    for error in errores:
        mensaje = error.casefold()
        campo = next(
            (
                nombre_campo
                for palabra, nombre_campo in campos_por_mensaje[paso]
                if palabra in mensaje
            ),
            None,
        )
        if campo is None:
            errores_sin_campo.append(error)
            continue

        campo_formulario = getattr(entry, campo)
        campo_formulario.errors = [*campo_formulario.errors, error]

    return errores_sin_campo


def _areas_aplicacion():
    return {
        value
        for value, _label in VacanteForm.area_aplicacion.kwargs["choices"]
        if value
    }


def _mes_anio_resumen(valor):
    if isinstance(valor, datetime):
        valor = valor.date()
    if not valor:
        return "—"
    meses = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    )
    return f"{meses[valor.month - 1]} {valor.year}"


def _duracion_experiencia_resumen(inicio, fin):
    if isinstance(inicio, datetime):
        inicio = inicio.date()
    if isinstance(fin, datetime):
        fin = fin.date()
    if not inicio or not fin or fin < inicio:
        return "—"

    meses = (fin.year - inicio.year) * 12 + fin.month - inicio.month
    if fin.day < inicio.day:
        meses -= 1
    meses = max(meses, 0)
    anos, meses_restantes = divmod(meses, 12)
    partes = []
    if anos:
        partes.append(f"{anos} año{'s' if anos != 1 else ''}")
    if meses_restantes:
        partes.append(f"{meses_restantes} mes{'es' if meses_restantes != 1 else ''}")
    return " y ".join(partes) if partes else "Menos de un mes"


def _asegurar_paso_maximo(usuario):
    paso = usuario.paso_maximo
    if paso in PASOS_seguimiento:
        return paso

    completitud = calcular_completitud_perfil(usuario.id)
    paso = completitud["primer_paso_faltante"] or PASOS_seguimiento[-1]
    usuario.paso_maximo = paso
    db.session.commit()
    return paso


def _avanzar_paso_maximo(paso):
    if paso not in PASOS_seguimiento:
        return

    paso_guardado = _asegurar_paso_maximo(current_user)
    idx_siguiente = PASOS_seguimiento.index(paso) + 1
    paso_alcanzado = (
        PASOS_seguimiento[idx_siguiente]
        if idx_siguiente < TOTAL_PASOS
        else paso
    )
    if PASOS_seguimiento.index(paso_alcanzado) > PASOS_seguimiento.index(paso_guardado):
        current_user.paso_maximo = paso_alcanzado
        db.session.commit()


@usuario_bp.before_request
def inicializar_paso_maximo():
    endpoint = request.endpoint.split(".")[-1] if request.endpoint else ""
    if not current_user.is_authenticated:
        return None

    if endpoint == "continuar_wizard":
        _asegurar_paso_maximo(current_user)
        return None

    if endpoint in PASOS_seguimiento:
        paso_maximo = _asegurar_paso_maximo(current_user)
        if PASOS_seguimiento.index(endpoint) > PASOS_seguimiento.index(paso_maximo):
            return redirect(url_for(f"usuario.{paso_maximo}"))

    return None



@usuario_bp.context_processor
def inject_progreso():
    endpoint = request.endpoint.split('.')[-1]
    if endpoint in PASOS_seguimiento:
        idx = PASOS_seguimiento.index(endpoint)
        paso_maximo = _asegurar_paso_maximo(current_user)
        paso_maximo_idx = PASOS_seguimiento.index(paso_maximo)
        return dict(
            nombre_paso=NOMBRES_PASO[endpoint],
            descripcion_paso=DESCRIPCIONES_PASO[endpoint],
            paso_actual=idx + 1,
            paso_habilitado_hasta=paso_maximo_idx + 1,
            total_pasos=TOTAL_PASOS,
            paso_anterior=PASOS_seguimiento[idx - 1] if idx > 0 else None,
            paso_siguiente=PASOS_seguimiento[idx + 1] if idx < TOTAL_PASOS - 1 else None,
            pasos_rutas=PASOS_seguimiento,
            nombres_cortos_pasos=NOMBRES_PASO,
        )
    return {"total_pasos": TOTAL_PASOS}


def redirigir_paso_wizard(paso_actual):
    _avanzar_paso_maximo(paso_actual)
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


@usuario_bp.route("/continuar")
@login_required
def continuar_wizard():
    paso = _asegurar_paso_maximo(current_user)
    return redirect(url_for(f"usuario.{paso}"))


@usuario_bp.route("/mi-hoja-de-vida", methods=["GET"])
@login_required
def mi_hoja_de_vida():
    id_usuario = current_user.id
    personal = Personal.query.filter_by(id_usuario=id_usuario).first()
    perfil_profesional = PerfilProfesional.query.filter_by(
        id_usuario=id_usuario
    ).first()
    funciones_perfil = FuncionArea.query.join(
        PerfilFuncion,
        PerfilFuncion.id_funcion == FuncionArea.id,
    ).filter(
        PerfilFuncion.id_usuario == id_usuario,
    ).order_by(FuncionArea.nombre).all()

    estudios = Info_academica.query.filter_by(
        id_usuario=id_usuario
    ).all()
    estudios.sort(
        key=lambda estudio: (
            estudio.estado == "en_curso",
            estudio.anno_finalizacion or 0,
            estudio.mes_finalizacion or 0,
        ),
        reverse=True,
    )

    experiencias = Experiencia.query.filter_by(
        id_usuario=id_usuario
    ).order_by(Experiencia.fecha_ingreso.desc()).all()
    cursos = Cursos.query.filter_by(
        id_usuario=id_usuario
    ).order_by(Cursos.fecha_realizacion.desc()).all()
    referencias = Referencias.query.filter_by(
        id_usuario=id_usuario
    ).order_by(Referencias.fecha_registro.desc()).all()
    referencias_personales = ReferenciasPersonales.query.filter_by(
        id_usuario=id_usuario
    ).order_by(ReferenciasPersonales.id.desc()).all()
    discapacidades = Discapacidades.query.filter_by(
        id_usuario=id_usuario
    ).order_by(Discapacidades.id.desc()).all()
    documentos = OtrosDocumentos.query.filter_by(
        id_usuario=id_usuario
    ).order_by(OtrosDocumentos.tipo, OtrosDocumentos.nombre).all()

    hoy = date.today()
    experiencias_resumen = []
    for experiencia_registro in experiencias[:4]:
        fecha_fin = (
            hoy
            if experiencia_registro.actual
            else experiencia_registro.fecha_salida
        )
        experiencias_resumen.append({
            "cargo": experiencia_registro.cargo or "—",
            "empresa": experiencia_registro.entidad or "—",
            "periodo": (
                f"{_mes_anio_resumen(experiencia_registro.fecha_ingreso)} a "
                f"{'Actual' if experiencia_registro.actual else _mes_anio_resumen(fecha_fin)}"
            ),
            "duracion": _duracion_experiencia_resumen(
                experiencia_registro.fecha_ingreso,
                fecha_fin,
            ),
        })

    tipos_documento = [
        valor
        for valor, etiqueta in documentoItemForm.tipo.kwargs["choices"]
        if valor
    ]
    tipos_cargados = {documento.tipo for documento in documentos}
    documentos_faltantes = [
        tipo for tipo in tipos_documento if tipo not in tipos_cargados
    ]

    completitud = calcular_completitud_perfil(id_usuario)
    pasos_urls = {
        "personal": url_for("usuario.personal"),
        "perfil_profesional": url_for("usuario.perfil_profesional"),
        "academica": url_for("usuario.academica"),
        "experiencia": url_for("usuario.experiencia"),
        "cursos": url_for("usuario.cursos"),
        "referencias": url_for("usuario.referencias"),
        "referencias_personales": url_for("usuario.referencias_personales"),
        "discapacidades": url_for("usuario.discapacidades"),
        "documentos": url_for("usuario.documentos"),
    }

    return render_template(
        "usuario/mi_hoja_de_vida.html",
        personal=personal,
        nombre_completo=(
            f"{personal.nombres} {personal.apellidos}".strip()
            if personal
            else f"{current_user.nombres} {current_user.apellidos}".strip()
        ),
        correo=current_user.correo,
        perfil_profesional=perfil_profesional,
        funciones_perfil=funciones_perfil,
        funciones_visibles=funciones_perfil[:8],
        funciones_adicionales=max(len(funciones_perfil) - 8, 0),
        estudios=estudios[:3],
        estudios_adicionales=max(len(estudios) - 3, 0),
        experiencias=experiencias_resumen,
        experiencias_adicionales=max(len(experiencias) - 4, 0),
        experiencia_total=formatear_experiencia(
            obtener_experiencia_total(id_usuario)
        ),
        cursos=cursos,
        referencias=referencias,
        referencias_personales=referencias_personales,
        discapacidades=discapacidades,
        documentos=documentos,
        documentos_faltantes=documentos_faltantes,
        completitud=completitud,
        secciones_faltantes=[
            (NOMBRES_PASO[paso], pasos_urls[paso])
            for paso, completa in completitud["secciones"].items()
            if not completa
        ],
        pasos_urls=pasos_urls,
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
    with current_app.open_resource("static/data/colombia.json") as catalog_file:
        colombia = json.load(catalog_file)

    form.departamento.choices = [("", "Seleccione")] + [
        (department, department) for department in colombia
    ]
    ubicacion_guardada_no_valida = False

    registro = Personal.query.filter_by(
        id_usuario=current_user.id
    ).first()

    if request.method == "POST":
        posted_department = request.form.get(form.departamento.name, "")
        form.municipio.choices = [("", "Seleccione")] + [
            (municipality, municipality)
            for municipality in colombia.get(posted_department, [])
        ]

        form_is_valid = form.validate()
        department = form.departamento.data
        municipality = form.municipio.data
        if municipality and municipality not in colombia.get(department, []):
            form.municipio.errors.append(
                "El municipio debe pertenecer al departamento seleccionado."
            )
            form_is_valid = False

        if form_is_valid:

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
        form.num_cel.data = registro.num_cel
        form.num_cel_dos.data = registro.num_cel_dos
        form.grupo_etnico.data = registro.grupo_etnico
        if registro.departamento in colombia:
            form.departamento.data = registro.departamento
            municipalities = colombia[registro.departamento]
        else:
            municipalities = []

        form.municipio.choices = [("", "Seleccione")] + [
            (municipality, municipality) for municipality in municipalities
        ]
        form.municipio.data = (
            registro.municipio if registro.municipio in municipalities else ""
        )
        ubicacion_guardada_no_valida = (
            bool(registro.departamento and registro.departamento not in colombia)
            or bool(
                registro.municipio
                and registro.municipio not in municipalities
            )
        )
        form.barrio.data = registro.barrio
        form.direccion.data = registro.direccion
        form.nacionalidad.data = registro.nacionalidad
        form.vive_rural.data = registro.vive_rural
        form.estado_civil.data = registro.estado_civil
        form.personas_cargo.data = registro.personas_cargo

    else:
        form.municipio.choices = [("", "Seleccione")]
        ubicacion_guardada_no_valida = False

    return render_template(
        "usuario/personal.html",
        form=form,
        ubicacion_guardada_no_valida=ubicacion_guardada_no_valida,
    )


@usuario_bp.route('/academica', methods=['GET', 'POST'])
@login_required
def academica():

    PASO_ACTUAL = "academica"
    form = InforAcademicaForm()
    mensaje_regla = None
    errores_formulario = []

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
        errores_formulario = []
        mensaje_regla = None
        hay_errores_fecha = False
        registros_guardados = Info_academica.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for entry in form.Info_academica:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_academica(entry)
            errores_negocio.extend(errores_fila)
            errores_formulario.extend(
                _asociar_errores_a_campos(entry, errores_fila, PASO_ACTUAL)
            )
            hay_errores_fecha = hay_errores_fecha or bool(
                entry.mes_finalizacion.errors
                or entry.anno_finalizacion.errors
            )

        if errores_negocio or hay_errores_fecha:
            pass

        else:
            if not _minimo_registros_cumplido(
                PASO_ACTUAL,
                form.Info_academica,
                campos,
                registros_guardados,
            ):
                mensaje_regla = REGLAS_PASO[PASO_ACTUAL]["mensaje"]

            if mensaje_regla is None:
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
                        registro.mes_finalizacion = (
                            entry.mes_finalizacion.data
                            if entry.estado.data == "finalizado"
                            else None
                        )
                        registro.anno_finalizacion = (
                            entry.anno_finalizacion.data
                            if entry.estado.data == "finalizado"
                            else None
                        )
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
                            mes_finalizacion=(
                                entry.mes_finalizacion.data
                                if entry.estado.data == "finalizado"
                                else None
                            ),
                            anno_finalizacion=(
                                entry.anno_finalizacion.data
                                if entry.estado.data == "finalizado"
                                else None
                            ),
                            intensidad_horaria=entry.intensidad_horaria.data,
                        )
                        db.session.add(nuevo)

                db.session.commit()
                return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/academica.html",
        form=form,
        anio_actual=datetime.now().year,
        mensaje_regla=mensaje_regla,
        errores_formulario=errores_formulario,
    )

@usuario_bp.route('/experiencia', methods=['GET', 'POST'])
@login_required
def experiencia():

    PASO_ACTUAL = "experiencia"
    form = experienciaForm()
    errores_negocio = []
    mensaje_regla = None
    no_tengo = _tiene_declaracion_paso(PASO_ACTUAL)

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
                "fecha_ingreso": registro.fecha_ingreso,
                "fecha_salida": registro.fecha_salida,
                "eliminar": "0",
            })

    if request.method == "POST":

        campos = ["entidad", "area", "cargo", "motivo", "fecha_ingreso", "fecha_salida"]  # ajusta a los campos obligatorios reales
        registros_guardados = Experiencia.query.filter_by(
            id_usuario=current_user.id
        ).all()
        if _declaracion_marcada(PASO_ACTUAL):
            _guardar_declaracion_paso(PASO_ACTUAL)
            db.session.commit()
            return redirigir_paso_wizard(PASO_ACTUAL)

        registros_por_id = {registro.id: registro for registro in registros_guardados}
        personal = Personal.query.filter_by(id_usuario=current_user.id).first()
        fecha_nacimiento = personal.fecha_nacimiento if personal else None

        for entry in form.Info_experiencia:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            try:
                registro_id = int(entry.registro_id.data)
            except (TypeError, ValueError):
                registro_id = None
            registro_existente = registros_por_id.get(registro_id)

            validar_rango_fechas = registro_existente is None
            if registro_existente:
                validar_rango_fechas = (
                    a_fecha(entry.fecha_ingreso.data)
                    != a_fecha(registro_existente.fecha_ingreso)
                    or a_fecha(entry.fecha_salida.data)
                    != a_fecha(registro_existente.fecha_salida)
                    or bool(entry.actual.data) != bool(registro_existente.actual)
                )

            errores_fila = validar_experiencia(
                entry,
                fecha_nacimiento=fecha_nacimiento,
                validar_rango_fechas=validar_rango_fechas,
            )
            errores_negocio.extend(errores_fila)

        if not errores_negocio and not _minimo_registros_cumplido(
            PASO_ACTUAL,
            form.Info_experiencia,
            campos,
            registros_guardados,
        ):
            mensaje_regla = REGLAS_PASO[PASO_ACTUAL]["mensaje"]

        if not errores_negocio and mensaje_regla is None:
            hoy = datetime.now().date()
            ids_eliminados = set()
            for entry in form.Info_experiencia:
                if entry.eliminar.data == "1":
                    try:
                        ids_eliminados.add(int(entry.registro_id.data))
                    except (TypeError, ValueError):
                        pass

            hay_cruce = False
            for entry in form.Info_experiencia:
                if entry.eliminar.data == "1" or fila_vacia(entry, campos):
                    continue

                fecha_ingreso = a_fecha(entry.fecha_ingreso.data)
                if not fecha_ingreso:
                    continue
                fecha_salida = (
                    hoy if entry.actual.data else a_fecha(entry.fecha_salida.data)
                )
                if not fecha_salida:
                    continue

                try:
                    registro_id = int(entry.registro_id.data)
                except (TypeError, ValueError):
                    registro_id = None

                for otra in registros_guardados:
                    if otra.id == registro_id or otra.id in ids_eliminados:
                        continue

                    otra_inicio = a_fecha(otra.fecha_ingreso)
                    otra_fin = (
                        hoy if otra.actual else a_fecha(otra.fecha_salida)
                    )
                    if rangos_se_cruzan(
                        fecha_ingreso,
                        fecha_salida,
                        otra_inicio,
                        otra_fin,
                    ):
                        hay_cruce = True
                        break

                if hay_cruce:
                    break

            if hay_cruce:
                flash(
                    "Aviso: el periodo de una experiencia se cruza con otra "
                    "experiencia registrada.",
                    "info",
                )

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
                    )
                    db.session.add(registro)

            if _hay_registro_valido_enviado(form.Info_experiencia, campos):
                _limpiar_declaracion_paso(PASO_ACTUAL)

            db.session.commit()

            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/experiencia.html",
        form=form,
        errores=errores_negocio,
        mensaje_regla=mensaje_regla,
        no_tengo=(
            no_tengo
            if request.method == "GET"
            else _declaracion_marcada(PASO_ACTUAL)
        ),
    )


@usuario_bp.route("/perfil-profesional", methods=["GET", "POST"])
@login_required
def perfil_profesional():
    registro = PerfilProfesional.query.filter_by(
        id_usuario=current_user.id
    ).first()
    errores = []
    csrf_form = FlaskForm()

    if request.method == "POST":
        csrf_valido = csrf_form.validate()
        area_aplicacion = request.form.get("area_aplicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        ids_enviados = request.form.getlist("funciones")

        if not csrf_valido:
            errores.extend(csrf_form.csrf_token.errors)

        if area_aplicacion not in _areas_aplicacion():
            errores.append("Selecciona un área de aplicación válida.")

        if len(descripcion) > 500:
            errores.append("La descripción no puede superar los 500 caracteres.")

        ids_funcion = set()
        ids_invalidos = False
        for id_enviado in ids_enviados:
            try:
                id_funcion = int(id_enviado)
            except (TypeError, ValueError):
                ids_invalidos = True
                continue
            if id_funcion <= 0:
                ids_invalidos = True
                continue
            ids_funcion.add(id_funcion)

        if ids_invalidos:
            errores.append("La selección de funciones contiene valores inválidos.")
        if not ids_funcion:
            errores.append("Selecciona al menos una función.")

        funciones_validas = []
        if area_aplicacion in _areas_aplicacion() and ids_funcion:
            funciones_validas = FuncionArea.query.filter(
                FuncionArea.id.in_(ids_funcion),
                FuncionArea.area_aplicacion == area_aplicacion,
                FuncionArea.activa.is_(True),
            ).all()
            if len(funciones_validas) != len(ids_funcion):
                errores.append(
                    "Cada función seleccionada debe estar activa y pertenecer "
                    "al área elegida."
                )

        if not errores:
            if registro is None:
                registro = PerfilProfesional(id_usuario=current_user.id)
                db.session.add(registro)

            registro.area_aplicacion = area_aplicacion
            registro.descripcion = descripcion or ""
            registro.actualizar()

            PerfilFuncion.query.filter_by(
                id_usuario=current_user.id
            ).delete(synchronize_session=False)
            for funcion in funciones_validas:
                db.session.add(
                    PerfilFuncion(
                        id_usuario=current_user.id,
                        id_funcion=funcion.id,
                    )
                )

            db.session.commit()
            return redirigir_paso_wizard("perfil_profesional")

        selected_ids = ids_funcion
        return render_template(
            "usuario/perfil_profesional.html",
            form=csrf_form,
            areas_aplicacion=VacanteForm.area_aplicacion.kwargs["choices"],
            area_seleccionada=area_aplicacion,
            descripcion=descripcion,
            funciones_seleccionadas=selected_ids,
            errores=errores,
        )

    funciones_seleccionadas = set()
    area_seleccionada = ""
    descripcion = ""
    if registro:
        area_seleccionada = registro.area_aplicacion
        descripcion = registro.descripcion or ""
        funciones_seleccionadas = {
            fila.id_funcion
            for fila in PerfilFuncion.query.filter_by(
                id_usuario=current_user.id
            ).all()
        }

    return render_template(
        "usuario/perfil_profesional.html",
        form=csrf_form,
        areas_aplicacion=VacanteForm.area_aplicacion.kwargs["choices"],
        area_seleccionada=area_seleccionada,
        descripcion=descripcion,
        funciones_seleccionadas=funciones_seleccionadas,
        errores=errores,
    )


@usuario_bp.route("/perfil-profesional/funciones", methods=["GET"])
@login_required
def perfil_profesional_funciones():
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    if area_aplicacion not in _areas_aplicacion():
        return jsonify({"error": "El área de aplicación no es válida."}), 400

    funciones = FuncionArea.query.filter_by(
        area_aplicacion=area_aplicacion,
        activa=True,
    ).order_by(FuncionArea.nombre.asc()).all()

    return jsonify({
        "funciones": [
            {"id": funcion.id, "nombre": funcion.nombre}
            for funcion in funciones
        ]
    })


@usuario_bp.route('/cursos', methods=['GET', 'POST'])
@login_required
def cursos():

    PASO_ACTUAL = "cursos"
    form = CursoForm()
    mensaje_regla = None
    errores_formulario = []

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
        errores_formulario = []
        registros_guardados = Cursos.query.filter_by(
            id_usuario=current_user.id
        ).all()

        if _declaracion_marcada(PASO_ACTUAL):
            _guardar_declaracion_paso(PASO_ACTUAL)
            db.session.commit()
            return redirigir_paso_wizard(PASO_ACTUAL)

        for entry in form.Info_curso:

            marcado_para_eliminar = entry.eliminar.data == "1"
            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_cursos(entry)
            errores_negocio.extend(errores_fila)
            errores_formulario.extend(
                _asociar_errores_a_campos(entry, errores_fila, PASO_ACTUAL)
            )

        if errores_negocio:
            pass

        elif not _minimo_registros_cumplido(
            PASO_ACTUAL,
            form.Info_curso,
            campos,
            registros_guardados,
        ):
            mensaje_regla = REGLAS_PASO[PASO_ACTUAL]["mensaje"]

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

            if _hay_registro_valido_enviado(form.Info_curso, campos):
                _limpiar_declaracion_paso(PASO_ACTUAL)

            db.session.commit()

            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/cursos.html",
        form=form,
        mensaje_regla=mensaje_regla,
        errores_formulario=errores_formulario,
        no_tengo=(
            _declaracion_marcada(PASO_ACTUAL)
            if request.method == "POST"
            else _tiene_declaracion_paso(PASO_ACTUAL)
        ),
    )

@usuario_bp.route('/referencias', methods=['GET', 'POST'])
@login_required
def referencias():

    PASO_ACTUAL = "referencias"
    form = referenciasForm()
    mensaje_regla = None
    errores_formulario = []

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
        errores_formulario = []
        registros_guardados = Referencias.query.filter_by(
            id_usuario=current_user.id
        ).all()

        if _declaracion_marcada(PASO_ACTUAL):
            _guardar_declaracion_paso(PASO_ACTUAL)
            db.session.commit()
            return redirigir_paso_wizard(PASO_ACTUAL)

        for entry in form.Info_referencias:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_referencias(entry)
            errores_negocio.extend(errores_fila)
            errores_formulario.extend(
                _asociar_errores_a_campos(entry, errores_fila, PASO_ACTUAL)
            )

        if errores_negocio:
            pass

        elif not _minimo_registros_cumplido(
            PASO_ACTUAL,
            form.Info_referencias,
            campos,
            registros_guardados,
        ):
            mensaje_regla = REGLAS_PASO[PASO_ACTUAL]["mensaje"]

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

            if _hay_registro_valido_enviado(form.Info_referencias, campos):
                _limpiar_declaracion_paso(PASO_ACTUAL)

            db.session.commit()
            flash("Guardado con éxito.", "success")
            return redirigir_paso_wizard(PASO_ACTUAL)

    return render_template(
        "usuario/referencias.html",
        form=form,
        mensaje_regla=mensaje_regla,
        errores_formulario=errores_formulario,
        no_tengo=(
            _declaracion_marcada(PASO_ACTUAL)
            if request.method == "POST"
            else PasoOmitido.query.filter_by(
                id_usuario=current_user.id,
                paso=PASO_ACTUAL,
            ).first() is not None
        ),
    )




@usuario_bp.route('/referencias_personales', methods=['GET', 'POST'])
@login_required
def referencias_personales():

    PASO_ACTUAL = "referencias_personales"
    form = referenciasPersonalesForm()
    mensaje_regla = None
    errores_formulario = []

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
        errores_formulario = []
        registros_guardados = ReferenciasPersonales.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for entry in form.Info_referencias_personales:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_referencias_personales(entry)
            errores_negocio.extend(errores_fila)
            errores_formulario.extend(
                _asociar_errores_a_campos(entry, errores_fila, PASO_ACTUAL)
            )

        if errores_negocio:
            pass

        elif not _minimo_registros_cumplido(
            PASO_ACTUAL,
            form.Info_referencias_personales,
            campos,
            registros_guardados,
        ):
            mensaje_regla = REGLAS_PASO[PASO_ACTUAL]["mensaje"]

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
        form=form,
        mensaje_regla=mensaje_regla,
        errores_formulario=errores_formulario,
    )

@usuario_bp.route('/discapacidades', methods=['GET', 'POST'])
@login_required
def discapacidades():

    PASO_ACTUAL = "discapacidades"
    form = discapacidadForm()
    errores_formulario = []

    def incluir_categoria_legada(entry, categoria):
        if (
            categoria
            and categoria in DISCAPACIDAD_CATEGORIAS_LEGADAS
            and categoria not in dict(entry.categoria.choices)
        ):
            entry.categoria.choices = [
                *entry.categoria.choices,
                (categoria, f"{categoria} (guardada anteriormente)"),
            ]

    if request.method == "GET":
        registros = Discapacidades.query.filter_by(
            id_usuario=current_user.id
        ).all()

        for registro in registros:
            entry = form.Info_discapacidades.append_entry({
                "registro_id": registro.id,
                "categoria": registro.categoria,
                "descripcion": registro.descripcion,
                "tiene_certificado": registro.tiene_certificado,
                "eliminar": "0",
            })
            incluir_categoria_legada(entry, registro.categoria)

    if request.method == "POST":
        for entry in form.Info_discapacidades:
            registro = Discapacidades.query.filter_by(
                id=entry.registro_id.data,
                id_usuario=current_user.id,
            ).first() if entry.registro_id.data else None
            if registro:
                incluir_categoria_legada(entry, registro.categoria)

        campos = [
            "categoria",
            "descripcion",
            "tiene_certificado"
        ]

        errores_negocio = []
        errores_formulario = []

        for entry in form.Info_discapacidades:

            marcado_para_eliminar = entry.eliminar.data == "1"

            if marcado_para_eliminar:
                continue

            if fila_vacia(entry, campos):
                continue

            errores_fila = validar_discapacidades(entry)
            errores_negocio.extend(errores_fila)
            errores_formulario.extend(
                _asociar_errores_a_campos(entry, errores_fila, PASO_ACTUAL)
            )

        if errores_negocio:
            pass

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
        form=form,
        DISCAPACIDAD_CATEGORIAS=DISCAPACIDAD_CATEGORIAS,
        errores_formulario=errores_formulario,
    )




@usuario_bp.route('/documentos', methods=['GET', 'POST'])
@login_required
def documentos() -> str | Response:
    form: documentoForm = documentoForm()

    if form.validate_on_submit():
        errores_archivo = []
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
                errores_archivo.append(
                    f"No se pudo guardar el archivo {nombre_original}."
                )
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
        if errores_archivo:
            docs: list[OtrosDocumentos] = OtrosDocumentos.query.filter_by(
                id_usuario=current_user.id
            ).order_by(OtrosDocumentos.fecha_registro.desc()).all()
            return render_template(
                "usuario/docs.html",
                form=form,
                docs=docs,
                errores_archivo=errores_archivo,
            )

        _avanzar_paso_maximo("documentos")
        db.session.commit()
        flash("Documentos guardados exitosamente.", "success")
        return redirect(url_for("usuario.registro_completo"))

    docs: list[OtrosDocumentos] = OtrosDocumentos.query.filter_by(
        id_usuario=current_user.id
    ).order_by(OtrosDocumentos.fecha_registro.desc()).all()

    return render_template("usuario/docs.html", form=form, docs=docs)


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
        flash("No se encontró el documento o no tienes permiso para eliminarlo.", "error")

    return redirect(url_for("usuario.documentos"))



@usuario_bp.route("/resumen", endpoint="resumen")
@usuario_bp.route("/registro-completo")
@login_required
def registro_completo():
    return render_template(
        "usuario/registro_completo.html",
        total_pasos=TOTAL_PASOS,
    )


### vacantes consultas sql filtros 

@usuario_bp.route('/vacantes/<int:id>', methods=["GET"])
@login_required
def detalle_vacante(id):
    vac = Vacante.query.get_or_404(id)
    requisitos_no_cumplidos = cumple_requisitos(current_user.id, vac)
    perfil_profesional = PerfilProfesional.query.filter_by(
        id_usuario=current_user.id
    ).first()
    return render_template(
        "detalle_vacante.html",
        vacante=vac,
        requisitos_no_cumplidos=requisitos_no_cumplidos,
        perfil_profesional_faltante=(
            perfil_profesional is None
            or not (perfil_profesional.area_aplicacion or "").strip()
        ),
    )

@usuario_bp.route('/vacantes', methods=["GET"])
@login_required
def vacantes():
    accion = request.args.get("accion", "")
    q = request.args.get("q", "").strip()
    area_aplicacion = request.args.get("area_aplicacion", "").strip()
    nivel = request.args.get("nivel", "").strip()
    estado = request.args.get("estado", "Activa")

    # Solo se aceptan los dos estados válidos; cualquier otro valor vuelve a "Activa"
    if estado not in ("Activa", "Cerrada"):
        estado = "Activa"

    page = request.args.get("page", 1, type=int)
    per_page = 12   # par, porque la cuadrícula es de 2 columnas

    query = Vacante.query.filter_by(estado=estado)

    if accion == "buscar":
        if q:
            query = query.filter(Vacante.titulo.ilike(f"%{q}%"))

    elif accion == "filtrar":
        if area_aplicacion:
            query = query.filter(Vacante.area_aplicacion == area_aplicacion)

        if nivel:
            query = query.filter(Vacante.nivel_academico == nivel)

    # El id desempata fechas iguales para que el orden entre páginas sea estable
    query = query.order_by(Vacante.fecha_publicacion.desc(), Vacante.id.desc())

    total = query.count()
    total_paginas = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_paginas))   # evita páginas fuera de rango

    vacantes = query.offset((page - 1) * per_page).limit(per_page).all()

    pagination = {
        "page": page,
        "pages": total_paginas,
        "total": total,
        "has_prev": page > 1,
        "has_next": page < total_paginas,
        "prev_num": page - 1,
        "next_num": page + 1,
    }

    areas_aplicacion = (
        VacanteForm
        .area_aplicacion
        .kwargs["choices"]
    )
    requisitos_por_vacante = {
        vacante.id: cumple_requisitos(current_user.id, vacante)
        for vacante in vacantes
    }
    perfil_profesional = PerfilProfesional.query.filter_by(
        id_usuario=current_user.id
    ).first()

    return render_template(
        "usuario/vacantes.html",
        vacantes=vacantes,
        pagination=pagination,
        areas=areas_aplicacion,
        q=q,
        area_aplicacion_seleccionada=area_aplicacion,
        nivel_seleccionado=nivel,
        requisitos_por_vacante=requisitos_por_vacante,
        perfil_profesional_faltante=(
            perfil_profesional is None
            or not (perfil_profesional.area_aplicacion or "").strip()
        ),
    )
@usuario_bp.route("/vacantes/<int:id>/postular", methods=["POST"])
@login_required
def postular(id):
    vac = Vacante.query.get_or_404(id)

    if vac.estado != "Activa":
        flash("Esta vacante ya no está disponible.", "error")
        return redirect(url_for("usuario.vacantes"))

    requisitos_no_cumplidos = cumple_requisitos(current_user.id, vac)
    if requisitos_no_cumplidos:
        perfil_profesional = PerfilProfesional.query.filter_by(
            id_usuario=current_user.id
        ).first()
        if (
            perfil_profesional is None
            or not (perfil_profesional.area_aplicacion or "").strip()
        ):
            flash(
                "Completa tu Perfil profesional antes de postularte.",
                "warning",
            )
            return redirect(url_for("usuario.perfil_profesional"))

        flash(" ".join(requisitos_no_cumplidos), "error")
        return redirect(url_for("usuario.vacantes"))

    completitud = calcular_completitud_perfil(current_user.id)

    if completitud["porcentaje"] < 100:
        flash(
            "Debes completar tu perfil antes de postularte. Te falta: "
            + ", ".join(completitud["faltantes"]) + ".",
            "warning"
        )
        return redirect(url_for("usuario.vacantes"))

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