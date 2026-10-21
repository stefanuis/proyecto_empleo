from datetime import datetime

from flask import Flask, flash, redirect, request, url_for
from flask_wtf.csrf import CSRFError

from .extensions import db, mail, login_manager, csrf
from .web import web_bp
from .usuario import usuario_bp
from .admin import admin_bp
from .web.admin_maestro  import admin_maestro_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Falta la variable SECRET_KEY en el archivo .env")

    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    app.register_blueprint(web_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_maestro_bp)


    login_manager.init_app(app)

    from .utils.formato import registrar_filtros
    registrar_filtros(app)

    from .utils.sesion import registrar_control_sesion
    registrar_control_sesion(app)

    @app.errorhandler(CSRFError)
    def csrf_invalido(error):
        flash("La sesión del formulario expiró. Intenta de nuevo.", "warning")
        return redirect(request.referrer or url_for("web.login"))

    ##me permite utilizar varibales globales

    @app.context_processor
    def dato_global():
        return{
            "anio": datetime.now().year,
            "version": "0.01",
            "titulo": "Principal mi Usuario",
            "LIMITES": {
            "academica": 4,
            "experiencia": 4,
            "cursos": 5,
            "referencias": 3,
            "referencias_personales": 3,
            "discapacidades": 3
           }
        }

    return app
