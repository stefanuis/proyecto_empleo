from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../templates/admin",
    static_folder="../static"
)


from . import principal
#from . import inicial
#from . import registro