from app.extensions import db


class VacanteFuncion(db.Model):
    """Funciones del catálogo (FuncionArea) que exige una vacante.

    Se comparan con las funciones del Perfil profesional del candidato
    (PerfilFuncion) para calcular la coincidencia.
    """
    __tablename__ = "tbl_vacante_funcion"
    __table_args__ = (
        db.UniqueConstraint(
            "id_vacante",
            "id_funcion",
            name="uq_vacante_funcion",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_vacante = db.Column(
        db.Integer,
        db.ForeignKey("tbl_vacante.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_funcion = db.Column(
        db.Integer,
        db.ForeignKey("tbl_funcion_area.id"),
        nullable=False,
    )
