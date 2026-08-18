from flask import Flask
from .extensions import db, mail, login_manager
from .web import web_bp
from .usuario import usuario_bp
from .admin import admin_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    #jwt.init_app(app)


    mail.init_app(app)

    app.register_blueprint(web_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(admin_bp)


    login_manager.init_app(app)
    #login_manager.login_view = "auth.login"

    #print(app.url_map)

    ##me permite utilizar varibales globales

    @app.context_processor
    def dato_global():
        return{
            "anio": 2026,
            "version": "0.01",
            "titulo": "Principal mi Usuario"
        }

    return app