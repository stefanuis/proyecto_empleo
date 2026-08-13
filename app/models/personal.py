from app.extensions import db
from datetime import datetime

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class Personal(db.Model):
    __tablename__ = "tbl_info_personal"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombres  = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    tipo_doc = db.Column(db.String(10))
    num_doc = db.Column(db.String(30))
    fecha_exp_doc = db.Column(db.DateTime)
    fecha_nacimiento = db.Column(db.DateTime)
    genero = db.Column(db.String(20))
    email   = db.Column(db.String(150))
    num_cel = db.Column(db.String(20))
    num_cel_dos = db.Column(db.String(20))
    grupo_etnico = db.Column(db.String(100))
    departamento = db.Column(db.String(50))
    municipio = db.Column(db.String(50))
    barrio = db.Column(db.String(50))
    direccion = db.Column(db.String(100))
    nacionalidad = db.Column(db.String(50))
    vive_rural = db.Column(db.String(10))
    estado_civil = db.Column(db.String(20))
    personas_cargo = db.Column(db.Integer)
    ultima_actualizacion = db.Column(db.DateTime)
    ruta_foto_perfil = db.Column(db.String(240))
    ruta_foto_doc = db.Column(db.String(240))


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"nombres: {self.nombres}"
        texto += f"apellidos: {self.apellidos}"
        texto += f"email: {self.email}"
        texto += f"num_cel: {self.num_cel}"

    



