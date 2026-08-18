from app.extensions import db
from datetime import datetime


class postulacion(db.Model):
    __tablename__ = "tbl_postulacion"
    id = db.Column(db.Integer, primary_key = True )
    id_usuario = db.Column(db.Integer)
    id_vacante = db.Column(db.Integer)
    estado = db.Column(db.String(30))
    notas_reclutador = db.Column(db.Text)
    fecha_postulacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"id_vacante: {self.id_vacante}"
        texto += f"estado: {self.estado}"
        texto += f"notas_reclutador: {self.notas_reclutador}"
        texto += f"fecha_postulacion: {self.fecha_postulacion}"
        texto += f"fecha_actualizacion: {self.fecha_actualizacion}"



