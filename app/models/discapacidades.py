from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Discapacidades(db.Model):
    __tablename__ = "tbl_discapacidades"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    categoria  = db.Column(db.String(50))
    descripcion = db.Column(db.String(250))
    ruta_certificado = db.Column(db.String(240))
    fecha_registro = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"categoria: {self.categoria}"
        texto += f"descripcion: {self.descripcion}"
        texto += f"ruta_certificado: {self.ruta_certificado}"