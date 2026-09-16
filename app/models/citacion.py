from app.extensions import db
from datetime import datetime

class Citaciones(db.Model):
    __tablename__="tbl_citacion"
    id = db.Column(db.Integer, primary_key=True)
    id_postulacion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    entrevistador = db.Column(db.String(100))
    estado = db.Column(db.String(30), default='pendiente')
    respuesta = db.Column(db.String(30))
    fecha_respuesta = db.Column(db.DateTime, default=datetime.now)
    token = db.Column(db.String(255), unique=True, index=True, nullable=True)
    token_envio = db.Column(db.DateTime)
