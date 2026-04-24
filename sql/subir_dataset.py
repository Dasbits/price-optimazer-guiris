"""
sql/subir_dataset.py
---------------------
Sube el fichero data/processed/dataset_integrado.csv a BigQuery como tabla
`<project>.datos.fact_ocupacion`.

Prerequisitos:
- `.env` con GOOGLE_APPLICATION_CREDENTIALS=credentials.json y BIGQUERY_PROJECT_ID.
- `credentials.json` (cuenta de servicio con rol BigQuery Data Editor + Job User).
- `data/processed/dataset_integrado.csv` generado por el notebook 04.

Ejecución (desde la raíz del proyecto, con el venv activado):
    python sql/subir_dataset.py

Flags opcionales:
    --dataset      Nombre del dataset BQ (default: datos)
    --table        Nombre de la tabla  (default: fact_ocupacion)
    --location     Región del dataset  (default: EU)
    --csv          Ruta al CSV         (default: data/processed/dataset_integrado.csv)
    --recreate     Si está presente, borra y recrea la tabla.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


# ──────────────────────────────────────────────────────────────────────────
# Rutas por defecto (relativas a la raíz del proyecto)
# ──────────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "processed" / "dataset_integrado.csv"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Carga dataset_integrado.csv en BigQuery.")
    p.add_argument("--dataset",  default="datos",            help="Dataset BQ destino")
    p.add_argument("--table",    default="fact_ocupacion",   help="Tabla BQ destino")
    p.add_argument("--location", default="EU",               help="Región del dataset")
    p.add_argument("--csv",      default=str(DEFAULT_CSV),   help="Ruta del CSV a subir")
    p.add_argument("--recreate", action="store_true",
                   help="Borra la tabla antes de subir (WRITE_TRUNCATE si existe).")
    return p.parse_args()


def get_bq_client(project_id: str | None) -> bigquery.Client:
    """Crea un cliente de BigQuery validando que hay credenciales."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        sys.exit("ERROR: GOOGLE_APPLICATION_CREDENTIALS no está en .env")
    creds_full = (ROOT / creds_path).resolve() if not os.path.isabs(creds_path) else Path(creds_path)
    if not creds_full.exists():
        sys.exit(f"ERROR: credenciales no encontradas en {creds_full}")
    # La librería lee la variable de entorno; nos aseguramos de apuntar al fichero correcto.
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_full)

    if not project_id:
        sys.exit("ERROR: BIGQUERY_PROJECT_ID no está en .env")

    return bigquery.Client(project=project_id)


def ensure_dataset(client: bigquery.Client, dataset_id: str, location: str) -> None:
    """Crea el dataset si no existe."""
    ref = bigquery.Dataset(f"{client.project}.{dataset_id}")
    ref.location = location
    try:
        client.get_dataset(ref)
        print(f"[OK] Dataset {client.project}.{dataset_id} ya existe.")
    except NotFound:
        client.create_dataset(ref, exists_ok=True)
        print(f"[NEW] Dataset {client.project}.{dataset_id} creado en {location}.")


def upload_csv(
    client: bigquery.Client,
    csv_path: Path,
    dataset_id: str,
    table_id: str,
    recreate: bool,
) -> bigquery.LoadJob:
    """Carga el CSV a la tabla indicada con auto-detección de esquema."""
    table_ref = f"{client.project}.{dataset_id}.{table_id}"

    if recreate:
        client.delete_table(table_ref, not_found_ok=True)
        print(f"[DEL] Tabla {table_ref} borrada (si existía).")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True,
        encoding="UTF-8",
    )

    print(f"[UP ] Subiendo {csv_path.name} ({csv_path.stat().st_size / 1024 / 1024:.1f} MB) → {table_ref}")
    with csv_path.open("rb") as fh:
        job = client.load_table_from_file(fh, table_ref, job_config=job_config)
    job.result()  # bloquea hasta que termina

    table = client.get_table(table_ref)
    print(f"[OK ] Carga completa: {table.num_rows:,} filas, {len(table.schema)} columnas.")
    return job


def main() -> None:
    args = parse_args()

    # 1. Cargar .env
    load_dotenv(ROOT / ".env")
    project_id = os.getenv("BIGQUERY_PROJECT_ID")

    # 2. Validar CSV
    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    if not csv_path.exists():
        sys.exit(f"ERROR: no existe {csv_path}. Ejecuta antes el notebook 04_integracion.ipynb.")

    # 3. Conectar a BigQuery
    client = get_bq_client(project_id)
    print(f"[CLI] Proyecto: {client.project} · Credenciales OK.")

    # 4. Asegurar dataset
    ensure_dataset(client, args.dataset, args.location)

    # 5. Subir CSV
    upload_csv(client, csv_path, args.dataset, args.table, args.recreate)

    # 6. Imprimir esquema detectado (útil para Power BI)
    table = client.get_table(f"{client.project}.{args.dataset}.{args.table}")
    print("\n--- Esquema detectado ---")
    for field in table.schema:
        print(f"  {field.name:<35} {field.field_type:<10} {field.mode}")

    print(f"\nTabla lista en BigQuery Studio:")
    print(f"  {client.project}.{args.dataset}.{args.table}")
    print("Power BI → Obtener datos → Google BigQuery → seleccionar proyecto y tabla.")


if __name__ == "__main__":
    main()
