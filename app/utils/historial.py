from datetime import datetime

from flask_login import current_user

from app.extensions import db
from app.models.postulacion_historial import PostulacionHistorial
from app.models.user import User


def registrar_evento(id_postulacion, accion, detalle=None, autor=True):
    """Agrega un evento al historial (no hace commit).

    autor=True usa al usuario con sesión iniciada; autor=None lo marca como
    evento del sistema (por ejemplo, la respuesta a una citación por correo).
    """
    id_autor = None
    if autor is True and current_user and current_user.is_authenticated:
        id_autor = current_user.id
    db.session.add(PostulacionHistorial(
        id_postulacion=id_postulacion,
        id_autor=id_autor,
        accion=accion,
        detalle=detalle,
        fecha=datetime.now(),
    ))


def historial_de(id_postulacion):
    """[(evento, nombre del autor o None)], del más reciente al más antiguo."""
    return db.session.query(
        PostulacionHistorial,
        User,
    ).outerjoin(
        User, User.id == PostulacionHistorial.id_autor
    ).filter(
        PostulacionHistorial.id_postulacion == id_postulacion
    ).order_by(
        PostulacionHistorial.fecha.desc(),
        PostulacionHistorial.id.desc(),
    ).all()
