import jwt
from datetime import datetime, timedelta

SECRET = "clave-super-secreta"

def generar_token(user_id):

    payload = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(hours=2)
    }

    return jwt.encode(payload, SECRET, algorithm="HS256")