from datetime import datetime

from app.extensions import db


class PerfilProfesional(db.Model):
    __tablename__ = "tbl_perfil_profesional"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, unique=True, nullable=False)
    area_aplicacion = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=True)

    def actualizar(self) -> None:
        self.fecha_actualizacion = datetime.now()
