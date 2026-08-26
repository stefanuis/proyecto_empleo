from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class OtrosDocumentos(db.Model):
    __tablename__ = "tbl_otros_docs"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    ruta_soporte = db.Column(db.String(240))
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombre: {self.nombre}"
        texto += f"ruta_soporte: {self.ruta_soporte}"
        texto += f"tipo: {self.tipo}"
