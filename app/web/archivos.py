import os

from flask import abort, send_file
from flask_login import current_user, login_required

from app.extensions import db
from app.models.discapacidades import Discapacidades
from app.models.docs import OtrosDocumentos
from app.utils.archivos import ruta_absoluta, se_muestra_en_linea

from . import web_bp

# tipo en la URL -> (modelo, columna con la ruta del archivo)
TIPOS_ARCHIVO = {
    "documento": (OtrosDocumentos, "ruta_soporte"),
    "certificado": (Discapacidades, "ruta_certificado"),
}


@web_bp.route("/archivos/<tipo>/<int:id>")
@login_required
def ver_archivo(tipo, id):
    """Entrega un archivo subido por un candidato.

    Solo lo puede ver su dueño o un administrador; para cualquier otro
    usuario responde 404, así no se revela si el archivo existe.
    """
    if tipo not in TIPOS_ARCHIVO:
        abort(404)
    modelo, columna = TIPOS_ARCHIVO[tipo]
    registro = db.session.get(modelo, id)

    if registro is None:
        abort(404)
    if current_user.rol != "admin" and registro.id_usuario != current_user.id:
        abort(404)

    ruta_relativa = getattr(registro, columna)
    ruta = ruta_absoluta(ruta_relativa)
    if ruta is None:
        abort(404)

    response = send_file(
        ruta,
        as_attachment=not se_muestra_en_linea(ruta_relativa),
        download_name=os.path.basename(ruta),
    )
    # Que el navegador no intente "adivinar" otro tipo de contenido
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, no-store"
    return response
