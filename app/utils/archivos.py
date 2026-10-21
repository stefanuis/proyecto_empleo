"""Archivos que suben los candidatos (documentos y certificados).

Se guardan en UPLOAD_FOLDER (fuera de static/) y en la base de datos queda la
ruta relativa, por ejemplo "uploads/docs/12_..._cedula.pdf".
"""
import os

from flask import current_app
from werkzeug.security import safe_join

# Se abren en el navegador; el resto (Word) se descarga
EXTENSIONES_EN_LINEA = {".pdf", ".jpg", ".jpeg", ".png"}


def ruta_absoluta(ruta_relativa):
    """Ruta en disco de un archivo subido, o None si no existe.

    safe_join impide que una ruta como "../../config.py" salga de la carpeta.
    """
    if not ruta_relativa:
        return None
    ruta = safe_join(current_app.config["UPLOAD_FOLDER"], ruta_relativa)
    if ruta and os.path.isfile(ruta):
        return ruta
    return None


def guardar_archivo(archivo, subcarpeta, nombre_final):
    """Guarda un FileStorage y devuelve la ruta relativa para la base de datos."""
    carpeta = os.path.join(current_app.config["UPLOAD_FOLDER"], "uploads", subcarpeta)
    os.makedirs(carpeta, exist_ok=True)
    archivo.save(os.path.join(carpeta, nombre_final))
    return f"uploads/{subcarpeta}/{nombre_final}"


def eliminar_archivo(ruta_relativa):
    ruta = ruta_absoluta(ruta_relativa)
    if ruta:
        os.remove(ruta)


def se_muestra_en_linea(ruta_relativa):
    return os.path.splitext(ruta_relativa or "")[1].lower() in EXTENSIONES_EN_LINEA
