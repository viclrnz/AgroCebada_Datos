"""
Lee el shapefile de parcelas y calcula el punto que la app usa como marcador.

El shapefile está en WGS84 (EPSG:4326), así que las coordenadas ya son
latitud y longitud. Se usa el centroide del polígono; si la parcela es
cóncava y el centroide cae fuera, se usa un punto interior para que el
marcador siempre quede dentro de la parcela.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import shapefile
from shapely.geometry import shape

from config import settings

log = logging.getLogger(__name__)

# Columnas del .dbf -> nombres del pipeline.
CAMPOS = {"ID_POLIGON": "id_poligono", "Municipio": "municipio", "Estado": "estado",
          "CONJUNTO": "conjunto", "área_ha": "area_ha_shp"}


def leer_parcelas(path: Path = settings.PARCELAS_PATH) -> pd.DataFrame:
    if not path.with_suffix(".shp").exists():
        raise FileNotFoundError(f"No se encontró el insumo: {path.with_suffix('.shp')}")
    prj = path.with_suffix(".prj")
    if prj.exists() and "WGS_1984" not in prj.read_text(encoding="utf-8"):
        raise ValueError(f"{prj.name} no está en WGS84; reproyecta antes de cargar.")

    filas, interiores = [], 0
    with shapefile.Reader(str(path), encoding="utf-8") as r:
        for sr in r.iterShapeRecords():
            geom = shape(sr.shape.__geo_interface__)
            punto = geom.centroid
            if not geom.contains(punto):
                punto = geom.representative_point()
                interiores += 1
            fila = {nuevo: sr.record[viejo] for viejo, nuevo in CAMPOS.items()}
            fila.update(latitud=punto.y, longitud=punto.x)
            filas.append(fila)

    df = pd.DataFrame(filas)
    df["id_poligono"] = df["id_poligono"].str.strip()
    log.info("Parcelas OK | %d polígonos | %d con punto interior en vez de centroide", len(df), interiores)
    return df
