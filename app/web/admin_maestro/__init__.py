from flask import Blueprint

admin_maestro_bp = Blueprint(
    "admin_maestro",
    __name__,
    url_prefix="/admin_maestro",
    template_folder="../templates/admin_maestro",
    static_folder="../static"
)


from . import principal
#from . import inicial
#from . import registro