from app.extensions import db


class FuncionArea(db.Model):
    __tablename__ = "tbl_funcion_area"

    id = db.Column(db.Integer, primary_key=True)
    area_aplicacion = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)
