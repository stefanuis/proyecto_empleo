from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Contacto(db.Model):
    __tablename__ = "tbl_contacto"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombre  = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    parentesco = db.Column(db.String(20))
    tel = db.Column(db.String(20))
    num_residencia = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombre: {self.nombre}"
        texto += f"apellido: {self.apellido}"
        texto += f"parentesco: {self.parentesco}"
