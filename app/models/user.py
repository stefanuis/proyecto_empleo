from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─────────────────────────────────────────────
#  MODELO: User
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "tbl_usuario"
    id = db.Column(db.Integer, primary_key=True)
    nombres  = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo   = db.Column(db.String(150), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20))
    clave_hash = db.Column(db.String(255), nullable=False)
    esta_activa     = db.Column(db.Boolean, default=False,  nullable=False)
    esta_verificada = db.Column(db.Boolean, default=False, nullable=False)
    fecha_creacion       = db.Column(db.DateTime, default=lambda: datetime.now())
    fecha_actualizacion  = db.Column(db.DateTime, default=lambda: datetime.now(),
                                     onupdate=lambda: datetime.now())
    ultimo_login         = db.Column(db.DateTime, nullable=True)  # None hasta que haga su 1er login
    rol = db.Column(db.String(50), default="usuario", nullable=False)

    token = db.Column(db.String(255), unique=True, index=True, nullable=True)
    token_envio = db.Column(db.DateTime)

    def set_password(self, clave_plana: str):
        """Recibe la contraseña en texto plano y guarda su hash."""
        self.clave_hash = generate_password_hash(clave_plana)

    def check_password(self, clave_plana: str) -> bool:
        """Compara una contraseña ingresada contra el hash almacenado.
        Devuelve True si coinciden, False si no.
        """
        return check_password_hash(self.clave_hash, clave_plana)

    # ─────────────────────────────────────────
    #  REPRESENTACIÓN
    #  Útil para debugging: print(user) → <User 1 - juan@mail.com>
    # ─────────────────────────────────────────
    def __repr__(self):
        texto = f"id: {self.id}"
        texto += f"nombres: {self.nombres}"
        texto += f"apellidos: {self.apellidos}"
        texto += f"correo: {self.correo}"
        texto += f"telefono: {self.telefono}"
        texto += f"esta_activa: {self.esta_activa}"
        texto += f"esta_verificada: {self.esta_verificada}"
        texto += f"fecha_creacion: {self.fecha_creacion}"
        texto += f"fecha_actualizacion: {self.fecha_actualizacion}"
        texto += f"ultimo_login: {self.ultimo_login}"
        texto += f"rol: {self.rol}"
    




