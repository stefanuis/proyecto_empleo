from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Citaciones(db.Model):
    __tablename__ = "tbl_citacion"
    id = db.Column(db.Integer, primary_key=True)
    id_postulacion = db.Column(db.Integer, db.ForeignKey("tbl_postulacion.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    lugar = db.Column(db.String(500))
    mensaje = db.Column(db.Text)
    estado = db.Column(db.String(30), default="pendiente")
    respuesta = db.Column(db.String(30))
    fecha_respuesta = db.Column(db.DateTime)
    token = db.Column(db.String(255), unique=True, index=True)
    fecha_envio = db.Column(db.DateTime)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_postulacion: {self.id_postulacion}"
        texto += f"fecha: {self.fecha}"
        texto += f"hora: {self.hora}"
        texto += f"lugar: {self.lugar}"
        texto += f"estado: {self.estado}"

        return texto
  


