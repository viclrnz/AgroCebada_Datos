"""
Normaliza los datos antes de cargarlos.

El ETL no imputa, escala ni selecciona variables. Esa lógica pertenece al
pipeline de sklearn para evitar fuga entre entrenamiento y predicción. Aquí
solo se estabilizan tipos y se conserva la trazabilidad de cada fila.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import pandas as pd

log = logging.getLogger(__name__)

# Conserva nulos sin convertir enteros y booleanos en float u object.
_DTYPES = {
    "bool": "boolean", "boolean": "boolean",
    "int64": "Int64", "Int64": "Int64",
    "float64": "float64",
    "str": "string", "object": "string", "string": "string",
}


def normalizar_tipos(df: pd.DataFrame, diccionario: pd.DataFrame) -> pd.DataFrame:
    """Alinea los tipos del dataframe con los definidos en el diccionario."""
    out = df.copy()
    for col, tipo in diccionario.set_index("columna")["tipo"].items():
        if col not in out.columns:
            continue
        destino = _DTYPES.get(tipo, tipo)
        if destino == "boolean" and not pd.api.types.is_bool_dtype(out[col]):
            out[col] = out[col].map({"True": True, "False": False, True: True, False: False}).astype("boolean")
        else:
            out[col] = out[col].astype(destino)
    return out


def transform(df: pd.DataFrame, diccionario: pd.DataFrame, fuente_sha256: str) -> tuple[pd.DataFrame, str]:
    out = normalizar_tipos(df, diccionario)

    # Quita espacios para que las claves de texto coincidan en los joins.
    for col in out.select_dtypes("string").columns:
        out[col] = out[col].str.strip()

    out = out.sort_values("id_poligono").reset_index(drop=True)

    # Guarda el origen y la ejecución que generó cada fila.
    run_id = str(uuid.uuid4())
    out["etl_run_id"] = run_id
    out["etl_cargado_en"] = datetime.now(timezone.utc)
    out["etl_fuente_sha256"] = fuente_sha256

    log.info("Transform OK | %d filas | run_id=%s", len(out), run_id)
    return out, run_id
