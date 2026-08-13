from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class familiar(db.Model):
    __tablename__ = "tbl_info_familiar"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    personas_casa  = db.Column(db.Integer)
    dependen_eco  = db.Column(db.Integer)
    fecha_realizacion = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"personas_casa: {self.personas_casa}"
        texto += f"dependen_eco: {self.dependen_eco}"
        texto += f"fecha_realizacion: {self.fecha_realizacion}"
