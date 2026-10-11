"""
Genera el DDL de la tabla destino a partir del diccionario de variables.

Así el esquema de Supabase se mantiene alineado con el entregable de datos.
"""
from __future__ import annotations

import pandas as pd

from config import settings

_PG_TIPOS = {
    "bool": "boolean", "boolean": "boolean",
    "int64": "integer", "Int64": "integer",
    "float64": "double precision",
    "str": "text", "object": "text", "string": "text",
}
NULLABLES = {"rendimiento_t_ha", "diag_y_redondo", "diag_y_resolucion"}


def ddl_matriz(diccionario: pd.DataFrame,
               tabla: str = settings.TABLA_DESTINO,
               esquema: str = settings.ESQUEMA_DESTINO) -> str:
    pk = settings.LLAVE_PRIMARIA
    lineas = []
    for _, fila in diccionario.iterrows():
        col, tipo = fila["columna"], _PG_TIPOS[fila["tipo"]]
        nulo = "" if col in NULLABLES else " NOT NULL"
        lineas.append(f"    {col:<28} {tipo}{nulo}")
    lineas += [
        f"    {'etl_run_id':<28} uuid NOT NULL",
        f"    {'etl_cargado_en':<28} timestamptz NOT NULL",
        f"    {'etl_fuente_sha256':<28} char(64) NOT NULL",
        f"    CONSTRAINT {tabla}_pk PRIMARY KEY ({pk})",
        f"    CONSTRAINT {tabla}_id_formato CHECK ({pk} ~ '^AGC_[0-9]{{3}}$')",
        f"    CONSTRAINT {tabla}_conjunto CHECK (conjunto IN ('ENTRENAMIENTO', 'PREDICCION'))",
        f"    CONSTRAINT {tabla}_objetivo CHECK ((conjunto = 'ENTRENAMIENTO') = (rendimiento_t_ha IS NOT NULL))",
    ]
    cuerpo = ",\n".join(lineas)
    comentarios = "\n".join(
        f"COMMENT ON COLUMN {esquema}.{tabla}.{f.columna} IS "
        f"'{f.rol} | {str(f.fuente).replace(chr(39), chr(39) * 2)} | {f.unidad}';"
        for f in diccionario.itertuples()
    )
    return f"CREATE TABLE IF NOT EXISTS {esquema}.{tabla} (\n{cuerpo}\n);\n\n{comentarios}\n"


if __name__ == "__main__":
    # Regenera el DDL con: python -m src.schema > sql/002_matriz_caracteristicas.sql
    print(ddl_matriz(pd.read_csv(settings.DICCIONARIO_PATH)))
