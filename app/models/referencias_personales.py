from app.extensions import db

class ReferenciasPersonales(db.Model):
    __tablename__ = "tbl_referencias_personales"
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    parentesco = db.Column(db.String(50))
    telefono = db.Column(db.String(20))

    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"id_usuario: {self.id_usuario}"
        texto += f"nombres: {self.nombres}"
        texto += f"apellidos: {self.apellidos}"
        texto += f"parentesco: {self.parentesco}"
        return texto