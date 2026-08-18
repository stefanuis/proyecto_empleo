from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Experiencia(db.Model):
    __tablename__ = "tbl_experiencia"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    entidad  = db.Column(db.String(100))
    area = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    actual = db.Column(db.Boolean)
    motivo = db.Column(db.String(100))
    otro = db.Column(db.String(250))
    fecha_ingreso = db.Column(db.DateTime)
    fecha_salida   = db.Column(db.DateTime)
    pais = db.Column(db.String(50))
    departamento = db.Column(db.String(50))
    municipio = db.Column(db.String(50))
    funciones_realizadas = db.Column(db.String(500)) #Cambiar esto a Texto.
    ruta_soporte = db.Column(db.String(240))
    fecha_registro = db.Column(db.DateTime)


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"entidad: {self.entidad}"
        texto += f"area: {self.area}"
        texto += f"cargo: {self.cargo}"