from datetime import datetime

from app.extensions import db


class PasoOmitido(db.Model):
    __tablename__ = "tbl_paso_omitido"
    __table_args__ = (
        db.UniqueConstraint(
            "id_usuario",
            "paso",
            name="uq_tbl_paso_omitido_usuario_paso",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    paso = db.Column(db.String(50), nullable=False)
    fecha_declaracion = db.Column(db.DateTime, default=datetime.now)
