import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "app" / "static" / "data"
DEPARTMENTS_COLUMN = "dpto"
MUNICIPALITY_COLUMN = "nom_mpio"
TYPE_COLUMN = "tipo_municipio"


def generate_catalog(input_csv: Path, output_json: Path) -> tuple[int, int, Counter]:
    catalog = {}
    record_types = Counter()

    with input_csv.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required_columns = {
            DEPARTMENTS_COLUMN,
            MUNICIPALITY_COLUMN,
            TYPE_COLUMN,
        }
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                f"El CSV debe contener las columnas {sorted(required_columns)}."
            )

        for line_number, row in enumerate(reader, start=2):
            department = (row[DEPARTMENTS_COLUMN] or "").strip()
            municipality = (row[MUNICIPALITY_COLUMN] or "").strip()
            record_type = (row[TYPE_COLUMN] or "").strip()
            if not department or not municipality or not record_type:
                raise ValueError(
                    f"Fila DIVIPOLA incompleta en la línea {line_number}."
                )

            municipalities = catalog.setdefault(department, [])
            if municipality not in municipalities:
                municipalities.append(municipality)
            record_types[record_type] += 1

    if len(catalog) != 33 or "BOGOTÁ, D.C." not in catalog:
        raise ValueError(
            "La fuente DIVIPOLA no contiene los 32 departamentos y Bogotá D.C."
        )

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(catalog), sum(map(len, catalog.values())), record_types


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera el catálogo de ubicaciones a partir de DIVIPOLA."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DATA_DIRECTORY / "divipola.csv",
        help="CSV oficial DIVIPOLA (por defecto, app/static/data/divipola.csv).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA_DIRECTORY / "colombia.json",
        help="JSON de salida (por defecto, app/static/data/colombia.json).",
    )
    args = parser.parse_args()

    department_count, location_count, record_types = generate_catalog(
        args.input, args.output
    )
    print(
        f"Generado {args.output}: {department_count} departamentos, "
        f"{location_count} ubicaciones DIVIPOLA. Tipos de origen: "
        + ", ".join(f"{name}: {count}" for name, count in sorted(record_types.items()))
    )


if __name__ == "__main__":
    main()
