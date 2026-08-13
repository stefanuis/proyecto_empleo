import jwt
from flask import request, jsonify

SECRET = "clave-super-secreta"

def requiere_jwt(f):

    def wrapper(*args, **kwargs):

        auth = request.headers.get("Authorization")

        if not auth:
            return jsonify({"error": "Token requerido"}), 401

        token = auth.split()[1]

        try:
            data = jwt.decode(token, SECRET, algorithms=["HS256"])
        except:
            return jsonify({"error": "Token inválido"}), 401

        request.user = data

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__

    return wrapper