#esto sivr epara ver si la base de datos se conecto


"""
seed_usuarios.py
────────────────
Script independiente para insertar usuarios de prueba en la BD.
No hace parte de la app; se corre una sola vez desde la terminal:

    python seed_usuarios.py

Requisitos:
    - La app Flask debe estar configurada (variables de entorno / config.py)
    - La tabla 'users' debe existir (haber corrido flask db upgrade)
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime, timezone

# ── Usuarios a insertar ───────────────────────────────────────
# Agrega o modifica los que necesites para tus pruebas.
USUARIOS_PRUEBA = [
    {
        "nombres":   "Laura",
        "apellidos": "Gómez",
        "correo":    "laura.gomez@ejemplo.com",
        "clave":     "Usuario1234",    # ← se cifrará automáticamente
        "telefono":  "3009876543",
        "rol":       "usuario",
        "esta_activa":     True,
        "esta_verificada": True,
    },
]


def seed():
    insertados = 0
    omitidos   = 0

    for datos in USUARIOS_PRUEBA:
        # Evita duplicados: si el correo ya existe, lo salta
        existe = User.query.filter_by(correo=datos["correo"]).first()
        if existe:
            print(f"  ⚠️  Omitido (ya existe): {datos['correo']}")
            omitidos += 1
            continue

        usuario = User(
            nombres          = datos["nombres"],
            apellidos        = datos["apellidos"],
            correo           = datos["correo"],
            telefono         = datos["telefono"],
            rol              = datos["rol"],
            esta_activa      = datos["esta_activa"],
            esta_verificada  = datos["esta_verificada"],
            fecha_creacion   = datetime.now(timezone.utc),
        )

        # set_password() cifra la clave con werkzeug antes de guardarla
        usuario.set_password(datos["clave"])

        db.session.add(usuario)
        print(f"  ✅ Listo para insertar: {datos['correo']}  |  rol: {datos['rol']}")
        insertados += 1

    db.session.commit()
    print(f"\n  Insertados: {insertados}  |  Omitidos: {omitidos}\n")


# ── Punto de entrada ─────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()          # Levanta el contexto de Flask (config, BD, etc.)
    with app.app_context():     # Necesario para que SQLAlchemy pueda acceder a la BD
        print("\n── Insertando usuarios de prueba ──────────────────")
        seed()
        print("── Listo ──────────────────────────────────────────\n")
