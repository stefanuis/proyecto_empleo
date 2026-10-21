import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _env_bool(nombre, por_defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")


class Config:
    # Sin valor por defecto: si falta en el .env la app no arranca (ver create_app)
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///dev.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sesión: se cierra sola tras este tiempo sin actividad
    SESION_INACTIVA_MINUTOS = int(os.getenv("SESION_INACTIVA_MINUTOS", "30"))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESION_INACTIVA_MINUTOS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # En producción con HTTPS: SESSION_COOKIE_SECURE=1 en el .env
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE")

    # Tamaño máximo de una petición (archivos subidos incluidos): 10 MB
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Documentos de los candidatos: fuera de static/ para que no sean públicos;
    # solo se descargan por la ruta /archivos/... que revisa permisos
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "archivos_privados"),
    )

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    # Remitente validado en Mailjet; si falta se usa el de app/utils/correo.py
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    # Dirección pública del sitio para los enlaces de los correos
    URL_PUBLICA = os.getenv("URL_PUBLICA")
