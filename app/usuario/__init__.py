from flask import Blueprint

usuario_bp = Blueprint(
    "usuario",
    __name__,
    url_prefix="/usuario",
    template_folder="../templates/usuario",
    static_folder="../static"
)


from . import principal
#from . import inicial
#from . import registro