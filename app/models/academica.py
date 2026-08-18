from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Info_academica(db.Model):
    __tablename__ = "tbl_info_academica"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    tipo  = db.Column(db.String(30))
    nivel = db.Column(db.String(100))
    estado = db.Column(db.String(30))
    periodos_cursados = db.Column(db.Integer)
    area = db.Column(db.String(30))
    titulo = db.Column(db.String(100))
    institucion = db.Column(db.String(100))
    pais_institucion   = db.Column(db.String(50))
    convalidacion = db.Column(db.Boolean)
    mes_finalizacion = db.Column(db.Integer)
    anno_finalizacion = db.Column(db.Integer)
    ruta_soporte = db.Column(db.String(240))
    intensidad_horaria = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"tipo: {self.tipo}"
        texto += f"nivel: {self.nivel}"
        texto += f"estado: {self.estado}"
