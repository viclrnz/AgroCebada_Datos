"""
Carga datos en Supabase de forma idempotente.

La carga usa upsert por bloques y una sola transacción. Solo actualiza filas
que cambiaron y registra cada ejecución en `etl_ejecuciones`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, MetaData, Table, inspect, select, text, tuple_
from sqlalchemy.dialects.postgresql import insert

from config import settings

log = logging.getLogger(__name__)
SQL_DIR = settings.ROOT_DIR / "sql"
COLS_METADATOS = {"etl_run_id", "etl_cargado_en", "etl_fuente_sha256"}


def _dividir_sentencias(sql: str) -> list[str]:
    """
    Separa sentencias para que pg8000 ejecute una por llamada.

    El separador ignora los `;` dentro de comillas, bloques `$$...$$` y
    comentarios SQL.
    """
    sentencias, actual, i = [], [], 0
    en_comilla = en_dolar = False
    while i < len(sql):
        c = sql[i]
        if not en_comilla and not en_dolar and sql.startswith("--", i):
            fin = sql.find("\n", i)
            i = len(sql) if fin == -1 else fin
            continue
        if not en_comilla and sql.startswith("$$", i):
            en_dolar = not en_dolar
            actual.append("$$")
            i += 2
            continue
        if not en_dolar and c == "'":
            en_comilla = not en_comilla
        if c == ";" and not en_comilla and not en_dolar:
            s = "".join(actual).strip()
            if s:
                sentencias.append(s)
            actual = []
        else:
            actual.append(c)
        i += 1
    resto = "".join(actual).strip()
    if resto:
        sentencias.append(resto)
    return sentencias


def aplicar_migraciones(engine: Engine, sql_dir: Path = SQL_DIR) -> None:
    """Aplica los scripts SQL en orden y dentro de una sola transacción."""
    with engine.begin() as conn:
        for archivo in sorted(sql_dir.glob("*.sql")):
            log.info("Migración | %s", archivo.name)
            for sentencia in _dividir_sentencias(archivo.read_text(encoding="utf-8")):
                conn.exec_driver_sql(sentencia)


def _a_registros(df: pd.DataFrame) -> list[dict]:
    """Convierte nulos y tipos de pandas al formato que acepta pg8000."""
    limpio = df.astype(object).where(df.notna(), None)
    return limpio.to_dict(orient="records")


def upsert(df: pd.DataFrame, engine: Engine,
           tabla: str = settings.TABLA_DESTINO,
           esquema: str = settings.ESQUEMA_DESTINO,
           chunk_size: int = settings.CHUNK_SIZE) -> int:
    pk = settings.LLAVE_PRIMARIA
    if not inspect(engine).has_table(tabla, schema=esquema):
        raise RuntimeError(f"No existe {esquema}.{tabla}. Ejecuta primero: python main.py init-db")

    t = Table(tabla, MetaData(), autoload_with=engine, schema=esquema)
    faltan = set(df.columns) - set(t.c.keys())
    if faltan:
        raise RuntimeError(f"La tabla destino no tiene las columnas {sorted(faltan)}; actualiza sql/ y migra.")

    cols_datos = [c for c in df.columns if c != pk and c not in COLS_METADATOS]
    registros = _a_registros(df)
    afectadas = 0

    with engine.begin() as conn:                       # Confirma al salir y revierte si falla.
        for i in range(0, len(registros), chunk_size):
            lote = registros[i:i + chunk_size]
            stmt = insert(t).values(lote)
            stmt = stmt.on_conflict_do_update(
                index_elements=[pk],
                set_={c: stmt.excluded[c] for c in df.columns if c != pk},
                where=tuple_(*[t.c[c] for c in cols_datos]).is_distinct_from(
                    tuple_(*[stmt.excluded[c] for c in cols_datos])
                ),
            )
            res = conn.execute(stmt)
            afectadas += res.rowcount
            log.debug("Chunk %d-%d | filas afectadas=%d", i, i + len(lote), res.rowcount)

        # No borramos parcelas ausentes del maestro; primero se reportan para revisión.
        en_bd = set(conn.execute(select(t.c[pk])).scalars())
        huerfanas = en_bd - set(df[pk])
        if huerfanas:
            log.warning("Hay %d parcelas en BD ausentes del maestro: %s", len(huerfanas), sorted(huerfanas)[:10])

    log.info("Load OK | %d filas enviadas | %d insertadas/actualizadas", len(registros), afectadas)
    return afectadas


def registrar_ejecucion(engine: Engine, **campos) -> None:
    """Registra el resultado en una transacción separada de la carga."""
    campos.setdefault("fin", datetime.now(timezone.utc))
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO public.etl_ejecuciones
                        (run_id, inicio, fin, estado, filas_fuente, filas_afectadas,
                         fuente_sha256, advertencias, mensaje)
                    VALUES (:run_id, :inicio, :fin, :estado, :filas_fuente, :filas_afectadas,
                            :fuente_sha256, :advertencias, :mensaje)
                """),
                campos,
            )
    except Exception:  # Un fallo de auditoría no debe ocultar el error original.
        log.exception("No se pudo registrar la ejecución en etl_ejecuciones")
