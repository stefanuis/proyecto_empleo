from datetime import datetime

from app.extensions import db


class PostulacionHistorial(db.Model):
    """Línea de tiempo de una postulación: quién hizo qué y cuándo.

    id_autor es None cuando el evento lo genera el sistema; si lo hace el
    candidato, es su propio id de usuario.
    """
    __tablename__ = "tbl_postulacion_historial"

    id = db.Column(db.Integer, primary_key=True)
    id_postulacion = db.Column(
        db.Integer,
        db.ForeignKey("tbl_postulacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_autor = db.Column(db.Integer, db.ForeignKey("tbl_usuario.id"), nullable=True)
    accion = db.Column(db.String(255), nullable=False)
    detalle = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
