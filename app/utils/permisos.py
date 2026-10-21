from flask import abort, url_for
from flask_login import current_user

from app.extensions import login_manager

# Panel de inicio de cada rol
PANEL_POR_ROL = {
    "admin_maestro": "admin_maestro.inicial",
    "admin": "admin.inicial",
    "usuario": "usuario.continuar_wizard",
}


def url_panel(rol):
    """URL del panel que le corresponde a un rol."""
    return url_for(PANEL_POR_ROL.get(rol, "usuario.continuar_wizard"))


def exigir_rol(*roles):
    """Corta la petición si el usuario no ha iniciado sesión o no tiene uno de los roles.

    Pensado para usarse en el before_request de un blueprint, así ninguna
    ruta nueva queda desprotegida por olvido.
    """
    if not current_user.is_authenticated:
        return login_manager.unauthorized()

    if current_user.rol not in roles:
        abort(403)

    return None
