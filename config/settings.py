"""
Configuración central del pipeline AgroCebada_Datos.

Las credenciales se leen desde `.env`, que no se versiona. La conexión usa
`pg8000` y SSL nativo porque es la combinación validada en Windows.
"""
from __future__ import annotations

import os
import ssl
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.pool import NullPool

# `config` está un nivel debajo de la raíz del proyecto.
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)
# Archivos de entrada entregados por el equipo de datos.
RAW_DIR = ROOT_DIR / "data" / "raw"
MAESTRO_PATH = RAW_DIR / "maestro_agrocebada.parquet"   # Fuente principal; conserva los tipos.
DICCIONARIO_PATH = RAW_DIR / "diccionario_variables.csv"
ROLES_PATH = RAW_DIR / "roles_columnas.json"
PARCELAS_PATH = RAW_DIR / "parcelas" / "Parcelas_Reto_AGC_CONJUNTO"   # Shapefile WGS84, sin extensión.
LOG_DIR = ROOT_DIR / "logs"
# Salidas de Modelado que consume la app.
PREDICTIONS_DIR = ROOT_DIR / "data" / "predictions"
COMPARACION_PATH = PREDICTIONS_DIR / "comparacion_modelos_rendimiento.csv"

# Parámetros de la tabla destino.
TABLA_DESTINO = os.getenv("ETL_TABLA_DESTINO", "matriz_caracteristicas")
ESQUEMA_DESTINO = os.getenv("ETL_ESQUEMA_DESTINO", "public")
LLAVE_PRIMARIA = "id_poligono"
CHUNK_SIZE = int(os.getenv("ETL_CHUNK_SIZE", "50"))
TABLA_RENDIMIENTOS = os.getenv("ETL_TABLA_RENDIMIENTOS", "rendimientos_estimados")
MODELO_VIGENTE = os.getenv("ETL_MODELO_VIGENTE", "ensamble_16vars")


@dataclass(frozen=True)
class DBSettings:
    host: str
    port: int
    user: str
    password: str
    database: str
    use_ssl: bool = True

    @classmethod
    def from_env(cls) -> "DBSettings":
        faltantes = [v for v in ("DB_HOST", "DB_USER", "DB_PASSWORD") if not os.getenv(v)]
        if faltantes:
            raise RuntimeError(
                f"Faltan variables de entorno: {faltantes}. Copia .env.example a .env y complétalo."
            )
        return cls(
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.getenv("DB_NAME", "postgres"),
            use_ssl=os.getenv("DB_SSL", "true").lower() == "true",
        )


def get_engine(settings: DBSettings | None = None) -> Engine:
    """Crea el engine batch sin mantener conexiones ociosas."""
    s = settings or DBSettings.from_env()
    url = URL.create(
        "postgresql+pg8000",
        username=s.user,
        password=s.password,   # URL.create escapa caracteres especiales.
        host=s.host,
        port=s.port,
        database=s.database,
    )
    if s.use_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args = {"ssl_context": ctx}
    else:
        connect_args = {}

    return create_engine(url, connect_args=connect_args, poolclass=NullPool, pool_pre_ping=True)