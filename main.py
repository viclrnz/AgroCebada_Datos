"""
Orquesta el pipeline AgroCebada_Datos.

Comandos:
    python main.py validar
    python main.py init-db
    python main.py run
    python main.py run --input otra/ruta/maestro.parquet --log-level DEBUG
    python main.py rendimientos
    python main.py rendimientos --modelo rf_12vars

Códigos de salida: 0 si termina bien, 1 ante un error inesperado y 2 si
el dataset no cumple el contrato.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from config.logging_config import setup_logging
from src.contracts import ContractError, exigir
from src.extract import extract
from src.transform import normalizar_tipos, transform

log = logging.getLogger("agrocebada.etl")


def cmd_validar(args) -> int:
    ins = extract(maestro_path=args.input)
    df = normalizar_tipos(ins.maestro, ins.diccionario)
    exigir(df, ins.diccionario, ins.roles)
    return 0


def cmd_init_db(args) -> int:
    from src.load import aplicar_migraciones
    aplicar_migraciones(settings.get_engine())
    log.info("Migraciones aplicadas")
    return 0


def cmd_run(args) -> int:
    from src.load import registrar_ejecucion, upsert

    engine = settings.get_engine()
    inicio = datetime.now(timezone.utc)
    bitacora = dict(run_id=None, inicio=inicio, filas_fuente=None, filas_afectadas=None,
                    fuente_sha256=None, advertencias=None)
    try:
        ins = extract(maestro_path=args.input)
        bitacora.update(filas_fuente=len(ins.maestro), fuente_sha256=ins.sha256)

        df = normalizar_tipos(ins.maestro, ins.diccionario)
        rep = exigir(df, ins.diccionario, ins.roles)
        bitacora["advertencias"] = len(rep.advertencias)

        df_final, run_id = transform(df, ins.diccionario, ins.sha256)
        bitacora["run_id"] = run_id

        bitacora["filas_afectadas"] = upsert(df_final, engine, chunk_size=args.chunk_size)
        registrar_ejecucion(engine, estado="OK", mensaje=None, **bitacora)
        return 0
    except ContractError as e:
        _registrar_fallo(engine, bitacora, "ERROR_CONTRATO", str(e))
        return 2
    except Exception as e:
        log.exception("Fallo del pipeline")
        _registrar_fallo(engine, bitacora, "ERROR", f"{type(e).__name__}: {e}")
        return 1


def cmd_rendimientos(args) -> int:
    import pandas as pd

    from src.extract import _sha256
    from src.load import registrar_ejecucion, upsert
    from src.parcelas import leer_parcelas
    from src.rendimientos import preparar_rendimientos, validar_comparacion, validar_parcelas

    engine = settings.get_engine()
    inicio = datetime.now(timezone.utc)
    bitacora = dict(run_id=None, inicio=inicio, filas_fuente=None, filas_afectadas=None,
                    fuente_sha256=None, advertencias=None)
    try:
        if not args.input.exists():
            raise FileNotFoundError(f"No se encontró el insumo: {args.input}")
        comparacion = pd.read_csv(args.input)
        huella = _sha256(args.input)
        bitacora.update(filas_fuente=len(comparacion), fuente_sha256=huella)

        maestro = extract().maestro
        parcelas = leer_parcelas(args.parcelas)
        validar_comparacion(comparacion, maestro, args.modelo)
        validar_parcelas(parcelas, maestro)
        df_final, run_id = preparar_rendimientos(comparacion, maestro, parcelas, args.modelo, huella)
        bitacora["run_id"] = run_id

        bitacora["filas_afectadas"] = upsert(df_final, engine, tabla=settings.TABLA_RENDIMIENTOS,
                                             chunk_size=args.chunk_size)
        registrar_ejecucion(engine, estado="OK", mensaje=f"rendimientos modelo={args.modelo}", **bitacora)
        return 0
    except ContractError as e:
        _registrar_fallo(engine, bitacora, "ERROR_CONTRATO", f"rendimientos: {e}")
        return 2
    except Exception as e:
        log.exception("Fallo de la carga de rendimientos")
        _registrar_fallo(engine, bitacora, "ERROR", f"rendimientos: {type(e).__name__}: {e}")
        return 1


def _registrar_fallo(engine, bitacora, estado, mensaje):
    import uuid
    from src.load import registrar_ejecucion
    bitacora["run_id"] = bitacora["run_id"] or str(uuid.uuid4())
    registrar_ejecucion(engine, estado=estado, mensaje=mensaje[:2000], **bitacora)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pipeline ETL AgroCebada → Supabase")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    sub = p.add_subparsers(dest="comando", required=True)

    for nombre, fn, ayuda in (
        ("validar", cmd_validar, "Valida el maestro contra el contrato (sin BD)"),
        ("init-db", cmd_init_db, "Crea/actualiza tablas y vistas en Supabase"),
        ("run", cmd_run, "Ejecuta el pipeline completo con upsert"),
        ("rendimientos", cmd_rendimientos, "Carga los rendimientos estimados que muestra la app"),
    ):
        sp = sub.add_parser(nombre, help=ayuda)
        sp.set_defaults(func=fn)
        if nombre in ("validar", "run"):
            sp.add_argument("--input", type=Path, default=settings.MAESTRO_PATH)
        if nombre == "rendimientos":
            sp.add_argument("--input", type=Path, default=settings.COMPARACION_PATH)
            sp.add_argument("--modelo", default=settings.MODELO_VIGENTE)
            sp.add_argument("--parcelas", type=Path, default=settings.PARCELAS_PATH,
                            help="Shapefile de parcelas sin extensión")
        if nombre in ("run", "rendimientos"):
            sp.add_argument("--chunk-size", type=int, default=settings.CHUNK_SIZE)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(args.log_level)
    try:
        return args.func(args)
    except ContractError:
        return 2
    except Exception:
        log.exception("Error no controlado")
        return 1


if __name__ == "__main__":
    sys.exit(main())
