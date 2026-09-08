from app.extensions import db
from datetime import datetime


class Vacante(db.Model):
    __tablename__ ="tbl_vacante"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150))
    area = db.Column(db.String(100))
    area_aplicacion = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    requisito = db.Column(db.Text)
    salario = db.Column(db.String())
    estado = db.Column(db.String(20)) 
    fecha_publicacion = db.Column(db.DateTime, default=datetime.now )
    fecha_cierre = db.Column(db.DateTime, default=datetime.now)
    id_usuario_creador = db.Column(db.Integer)
    nivel_academico = db.Column(db.String(45))
    area_aplicacion = db.Column(db.String(45))


    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"titulo: {self.titulo}"
        texto += f"area: {self.area}"
        texto += f"requisito: {self.requisito}"
        texto += f"salario: {self.salario}"
        texto += f"fecha_publicacion: {self.fecha_publicacion}"
        texto += f"fecha_cierre: {self.fecha_cierre}"
        texto += f"id_usuario_creador: {self.id_usuario_creador}"