import json
from pathlib import Path

from app import create_app
from app.extensions import db
from app.forms.vacante import VacanteForm
from app.models.funcion_area import FuncionArea


JSON_PATH = Path(__file__).resolve().parent / "data" / "funciones_por_area.json"


def main() -> None:
    if not JSON_PATH.is_file():
        raise SystemExit(
            f"No se encontró el archivo de funciones. Ruta esperada: {JSON_PATH}"
        )

    with JSON_PATH.open(encoding="utf-8") as source:
        catalog = json.load(source)

    if not isinstance(catalog, dict):
        raise ValueError("El JSON debe ser un objeto de áreas y listas de funciones.")

    valid_areas = {
        value
        for value, _label in VacanteForm.area_aplicacion.kwargs["choices"]
        if value
    }
    for area in catalog:
        if area not in valid_areas:
            print(f"Advertencia: el área del JSON no está en VacanteForm: {area}")

    app = create_app()
    insertadas = 0
    omitidas = 0
    totales_por_area = {}
    insertadas_por_area = {}
    omitidas_por_area = {}

    with app.app_context():
        existentes = {
            (area, funcion)
            for area, funcion in db.session.query(
                FuncionArea.area_aplicacion,
                FuncionArea.nombre,
            ).all()
        }

        for area, funciones in catalog.items():
            if not isinstance(area, str) or not isinstance(funciones, list):
                raise ValueError(
                    "Cada clave del JSON debe ser un área y su valor una lista."
                )

            totales_por_area[area] = len(funciones)
            insertadas_por_area[area] = 0
            omitidas_por_area[area] = 0

            for funcion in funciones:
                if not isinstance(funcion, str) or not funcion.strip():
                    raise ValueError(
                        f"El área {area!r} contiene una función vacía o inválida."
                    )

                clave = (area, funcion)
                if clave in existentes:
                    omitidas += 1
                    omitidas_por_area[area] += 1
                    continue

                db.session.add(
                    FuncionArea(
                        area_aplicacion=area,
                        nombre=funcion,
                    )
                )
                existentes.add(clave)
                insertadas += 1
                insertadas_por_area[area] += 1

        db.session.commit()

    print(f"Insertadas: {insertadas}")
    print(f"Omitidas: {omitidas}")
    print("Totales por área:")
    for area, total in totales_por_area.items():
        print(
            f"- {area}: insertadas {insertadas_por_area[area]}, "
            f"omitidas {omitidas_por_area[area]}, total {total}"
        )


if __name__ == "__main__":
    main()
