"""Configura el log de consola y el archivo rotativo `logs/etl.log`."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(nivel: str = "INFO") -> None:
    LOG_DIR.mkdir(exist_ok=True)
    raiz = logging.getLogger()
    raiz.setLevel(nivel.upper())
    raiz.handlers.clear()

    consola = logging.StreamHandler()
    consola.setFormatter(logging.Formatter(FORMATO, "%H:%M:%S"))

    archivo = RotatingFileHandler(
        LOG_DIR / "etl.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    archivo.setFormatter(logging.Formatter(FORMATO))

    raiz.addHandler(consola)
    raiz.addHandler(archivo)
    # Los mensajes normales de SQLAlchemy no aportan al log del pipeline.
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
