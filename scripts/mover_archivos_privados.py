"""Mueve los archivos subidos por los candidatos de app/static/uploads (público)
a la carpeta privada UPLOAD_FOLDER (por defecto archivos_privados/).

La ruta guardada en la base de datos ("uploads/docs/...") no cambia, así que no
hay que tocar la base. Se puede correr varias veces: si un archivo ya existe en
el destino, no lo sobrescribe.

    python scripts/mover_archivos_privados.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


def main() -> None:
    app = create_app()
    origen = os.path.join(app.root_path, "static", "uploads")
    destino = os.path.join(app.config["UPLOAD_FOLDER"], "uploads")

    if not os.path.isdir(origen):
        print(f"No hay archivos públicos que mover ({origen} no existe).")
        return

    movidos = omitidos = 0
    for carpeta, _subcarpetas, archivos in os.walk(origen):
        relativa = os.path.relpath(carpeta, origen)
        carpeta_destino = os.path.normpath(os.path.join(destino, relativa))
        os.makedirs(carpeta_destino, exist_ok=True)
        for nombre in archivos:
            ruta_destino = os.path.join(carpeta_destino, nombre)
            if os.path.exists(ruta_destino):
                print(f"  Omitido (ya existe en destino): {os.path.join(relativa, nombre)}")
                omitidos += 1
                continue
            shutil.move(os.path.join(carpeta, nombre), ruta_destino)
            movidos += 1

    # Quita las carpetas que quedaron vacías en static/uploads
    for carpeta, _subcarpetas, _archivos in sorted(os.walk(origen), reverse=True):
        if not os.listdir(carpeta):
            os.rmdir(carpeta)

    print(f"Movidos: {movidos} | Omitidos: {omitidos}")
    print(f"Carpeta privada: {destino}")


if __name__ == "__main__":
    main()
