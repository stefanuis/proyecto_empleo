from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class referencias(db.Model):
    __tablename__ = "tbl_referencias"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombres  = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    parentesco = db.Column(db.String(30))
    empresa = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    ciudad = db.Column(db.String(30))
    autoriza = db.Column(db.String(10))
    fecha_registro = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombres: {self.nombres}"
        texto += f"apellidos: {self.apellidos}"
        texto += f"parentesco: {self.parentesco}"