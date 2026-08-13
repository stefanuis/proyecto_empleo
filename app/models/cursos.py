from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Cursos(db.Model):
    __tablename__ = "tbl_cursos"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombre  = db.Column(db.String(150), nullable=False)
    institucion = db.Column(db.String(150), nullable=False)
    area = db.Column(db.String(150))
    horas = db.Column(db.Integer)
    fecha_realizacion = db.Column(db.DateTime)
    certificado = db.Column(db.Boolean)
    fecha_realizacion = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombre: {self.nombre}"
        texto += f"institucion: {self.institucion}"
        texto += f"area: {self.area}"



  #ruta de cursos
  


