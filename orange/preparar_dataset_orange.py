"""
orange/preparar_dataset_orange.py
----------------------------------
Genera dos CSV listos para alimentar Orange Data Mining:

    data/processed/train.csv   (días < 2026-01-25, ~75% del horizonte)
    data/processed/test.csv    (días >= 2026-01-25, ~25%)

Replica el feature engineering del notebook 05_modelado.ipynb:

  · Drop de columnas con leakage (availability_*, estimated_occupancy_l365d).
  · Drop de identificadores irrelevantes (listing_id, date) tras usarlos
    para construir target encodings.
  · Target encoding por barrio        → neigh_enc      (calculado SOLO en train).
  · Target encoding por listing_id    → listing_te     (calculado SOLO en train).
  · One-hot encoding de room_type, property_type, weather_cat,
    neighbourhood_group_cleansed.
  · Conversión de booleanos a int.
  · La columna `occupied` queda intacta como target en ambos CSV.

Uso (desde la raíz del repo, con el venv activo):
    python orange/preparar_dataset_orange.py

Flags:
    --csv-in     ruta al dataset integrado (default: data/processed/dataset_integrado.csv)
    --out-dir    carpeta de salida          (default: data/processed)
    --split      fecha de corte             (default: 2026-01-25)

Autor: Dasbits (IFP España, Big Data e IA, 2025-2026)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────
# Rutas por defecto
# ──────────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parents[1]
CSV_IN   = ROOT / "data" / "processed" / "dataset_integrado.csv"
OUT_DIR  = ROOT / "data" / "processed"

# Columnas a eliminar siempre del feature set
LEAKAGE_COLS = [
    "availability_30", "availability_60", "availability_90", "availability_365",
    "estimated_occupancy_l365d",
]
ID_COLS = ["listing_id", "date"]   # ya no aportan tras el target encoding
LOW_VALUE_COLS = ["minimum_nights_day", "maximum_nights_day"]

# Columnas categóricas one-hot
ONEHOT_COLS = [
    "room_type",
    "property_type",
    "weather_cat",
    "neighbourhood_group_cleansed",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Genera train/test para Orange.")
    p.add_argument("--csv-in",  default=str(CSV_IN),  help="Ruta al dataset integrado.")
    p.add_argument("--out-dir", default=str(OUT_DIR), help="Carpeta de salida.")
    p.add_argument("--split",   default="2026-01-25",
                   help="Fecha de corte train/test (YYYY-MM-DD).")
    return p.parse_args()


def load(csv_in: Path) -> pd.DataFrame:
    if not csv_in.exists():
        sys.exit(f"ERROR: no existe {csv_in}. Ejecuta antes el notebook 04.")
    df = pd.read_csv(csv_in, parse_dates=["date"])
    print(f"[IN ] Cargado {csv_in.name}: {df.shape[0]:,} filas × {df.shape[1]} cols")
    return df


def split_by_date(df: pd.DataFrame, split: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["date"] <  split].copy()
    test  = df[df["date"] >= split].copy()
    print(f"[SPL] Split {split.date()}: train={train.shape[0]:,}  test={test.shape[0]:,}")
    return train, test


def add_target_encodings(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula los TE solo con train para evitar leakage hacia test."""
    global_mean = train["occupied"].mean()

    # neigh_enc
    nbh_map = train.groupby("neighbourhood_cleansed")["occupied"].mean()
    train["neigh_enc"] = train["neighbourhood_cleansed"].map(nbh_map).fillna(global_mean)
    test["neigh_enc"]  = test["neighbourhood_cleansed"].map(nbh_map).fillna(global_mean)

    # listing_te
    listing_map = train.groupby("listing_id")["occupied"].mean()
    train["listing_te"] = train["listing_id"].map(listing_map).fillna(global_mean)
    test["listing_te"]  = test["listing_id"].map(listing_map).fillna(global_mean)

    # Sanity: cuántos listings de test no estaban en train
    new_in_test = set(test["listing_id"]) - set(train["listing_id"])
    print(f"[TE ] global_mean={global_mean:.4f}  "
          f"barrios_train={nbh_map.size}  listings_train={listing_map.size}  "
          f"listings_cold_start_en_test={len(new_in_test)}")
    return train, test


def encode_and_drop(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot, drop de columnas no-feature y conversión bool→int."""
    drop_cols = LEAKAGE_COLS + ID_COLS + LOW_VALUE_COLS + ["neighbourhood_cleansed"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)

    # One-hot. drop_first=False para que Orange tenga todas las categorías visibles.
    onehot = [c for c in ONEHOT_COLS if c in df.columns]
    df = pd.get_dummies(df, columns=onehot, drop_first=False)

    # bool → int (Orange los lee mejor)
    bool_cols = df.select_dtypes(include="bool").columns
    df[bool_cols] = df[bool_cols].astype(int)

    return df


def align(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Garantiza que train y test tienen las mismas columnas en el mismo orden."""
    cols = sorted(set(train.columns) | set(test.columns))
    # `occupied` siempre primero por convención (Orange selecciona target en GUI igualmente)
    cols = ["occupied"] + [c for c in cols if c != "occupied"]
    train = train.reindex(columns=cols, fill_value=0)
    test  = test.reindex(columns=cols, fill_value=0)
    return train, test


def main() -> None:
    args = parse_args()
    csv_in  = Path(args.csv_in)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    split   = pd.Timestamp(args.split)

    df = load(csv_in)
    train, test = split_by_date(df, split)
    train, test = add_target_encodings(train, test)

    # Aplicamos drop+encoding a cada uno por separado y luego alineamos
    train_enc = encode_and_drop(train)
    test_enc  = encode_and_drop(test)
    train_enc, test_enc = align(train_enc, test_enc)

    # Tipos: todo numérico (target encoding + onehot + numéricas originales)
    # Convertimos lo que pueda haber quedado como object
    for c in train_enc.columns:
        if train_enc[c].dtype == "object":
            train_enc[c] = pd.to_numeric(train_enc[c], errors="coerce").fillna(0)
            test_enc[c]  = pd.to_numeric(test_enc[c],  errors="coerce").fillna(0)

    out_train = out_dir / "train.csv"
    out_test  = out_dir / "test.csv"
    train_enc.to_csv(out_train, index=False)
    test_enc.to_csv(out_test,  index=False)

    print()
    print(f"[OUT] train.csv  →  {train_enc.shape[0]:>9,} filas × {train_enc.shape[1]} cols")
    print(f"[OUT] test.csv   →  {test_enc.shape[0]:>9,} filas × {test_enc.shape[1]} cols")
    print(f"[OUT] target balance train: {train_enc['occupied'].mean()*100:.2f}% ocupado")
    print(f"[OUT] target balance test : {test_enc['occupied'].mean()*100:.2f}% ocupado")
    print()
    print(f"[OK ] Ficheros listos para Orange en {out_dir}/")
    print("     · {0}".format(out_train))
    print("     · {0}".format(out_test))


if __name__ == "__main__":
    main()
