
#Ese código es el punto de entrada para ejecutar una aplicación web hecha con Flask.

import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    # El modo debug permite ejecutar código desde el navegador si ocurre un error,
    # por eso solo se activa de forma explícita con FLASK_DEBUG=1 en el .env

    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1",
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=9911,
    )
