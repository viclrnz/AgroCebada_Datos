"""
Lee los entregables de preprocesamiento.

El Parquet es la fuente principal porque conserva booleanos nulos. El CSV
queda como alternativa para auditoría y se re-tipifica después.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import settings

log = logging.getLogger(__name__)


@dataclass
class Insumos:
    maestro: pd.DataFrame
    diccionario: pd.DataFrame
    roles: dict[str, list[str]]
    sha256: str  # Identifica el archivo usado en esta carga.


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def extract(
    maestro_path: Path = settings.MAESTRO_PATH,
    diccionario_path: Path = settings.DICCIONARIO_PATH,
    roles_path: Path = settings.ROLES_PATH,
) -> Insumos:
    for p in (maestro_path, diccionario_path, roles_path):
        if not p.exists():
            raise FileNotFoundError(f"No se encontró el insumo: {p}")

    if maestro_path.suffix == ".parquet":
        maestro = pd.read_parquet(maestro_path)
    else:
        log.warning("Leyendo CSV: los tipos nulos (boolean/Int64) se re-tipifican en transform.")
        maestro = pd.read_csv(maestro_path)

    diccionario = pd.read_csv(diccionario_path)
    roles = json.loads(roles_path.read_text(encoding="utf-8"))
    huella = _sha256(maestro_path)

    log.info(
        "Extract OK | maestro=%s filas x %s cols | sha256=%s…",
        *maestro.shape, huella[:12],
    )
    return Insumos(maestro, diccionario, roles, huella)
