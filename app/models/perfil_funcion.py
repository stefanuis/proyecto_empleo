from app.extensions import db


class PerfilFuncion(db.Model):
    __tablename__ = "tbl_perfil_funcion"
    __table_args__ = (
        db.UniqueConstraint(
            "id_usuario",
            "id_funcion",
            name="uq_usuario_funcion",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_funcion = db.Column(db.Integer, nullable=False)
