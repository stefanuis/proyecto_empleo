from app.extensions import db

class FuncionExperiencia(db.Model):
    __tablename__ = "tbl_funcion_experiencia"

    id = db.Column(db.Integer, primary_key=True)
    id_experiencia = db.Column(
        db.Integer,
        db.ForeignKey("tbl_experiencia.id", ondelete="CASCADE"),
        nullable=False
    )
    funcion = db.Column(db.String(150), nullable=False)