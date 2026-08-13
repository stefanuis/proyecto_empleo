from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Docs(db.Model):
    __tablename__ = "tbl_docs"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombre  = db.Column(db.String(50))
    ruta = db.Column(db.String(254))
    tipo = db.Column(db.String(50))
    fecha_actualizacion = db.Column(db.DateTime)
    


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombre: {self.nombre}"
        texto += f"ruta: {self.ruta}"
        texto += f"tipo: {self.tipo}"