from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Competencias(db.Model):
    __tablename__ = "tbl_competencias"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    competencia  = db.Column(db.String(150))
    nivel = db.Column(db.String(50))
    experiencia = db.Column(db.Integer)
    fecha_actualizacion = db.Column(db.DateTime)
    


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"competencia: {self.competencia}"
        texto += f"nivel: {self.nivel}"
        texto += f"experiencia: {self.experiencia}"