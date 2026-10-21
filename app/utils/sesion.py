"""Control de la sesión: cierre por inactividad y páginas privadas sin caché."""
import time

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user

from app.utils.permisos import url_panel

# Rutas que no cuentan como actividad ni se revisan (archivos estáticos)
ENDPOINTS_SIN_CONTROL = {"static"}


def _tiempo_limite():
    return current_app.config["SESION_INACTIVA_MINUTOS"] * 60


def cerrar_sesion():
    logout_user()
    session.clear()


def registrar_control_sesion(app):

    @app.before_request
    def controlar_inactividad():
        endpoint = request.endpoint or ""
        if endpoint in ENDPOINTS_SIN_CONTROL or endpoint.endswith(".static"):
            return None
        if not current_user.is_authenticated:
            return None

        ahora = time.time()
        ultima = session.get("ultima_actividad")
        if ultima is not None and ahora - ultima > _tiempo_limite():
            cerrar_sesion()
            flash("Tu sesión se cerró por inactividad. Vuelve a iniciar sesión.", "warning")
            return redirect(url_for("web.login"))

        # La cookie de sesión vence con el mismo tiempo y se renueva en cada petición
        session.permanent = True
        session["ultima_actividad"] = ahora
        return None

    @app.after_request
    def no_guardar_paginas_privadas(response):
        # Sin esto, tras cerrar sesión el botón "Atrás" mostraba páginas
        # privadas desde la memoria del navegador
        if current_user.is_authenticated and response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    @app.errorhandler(403)
    def acceso_denegado(error):
        destino = url_panel(current_user.rol) if current_user.is_authenticated else url_for("web.login")
        return render_template("error_403.html", destino=destino), 403

    @app.context_processor
    def datos_sesion():
        return {"sesion_inactiva_minutos": current_app.config["SESION_INACTIVA_MINUTOS"]}
