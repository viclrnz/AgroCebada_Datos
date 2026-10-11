"""
Valida el contrato de datos del maestro.

Los errores detienen la carga. Las advertencias quedan en el log y permiten
continuar. El contrato se toma del diccionario y de los roles de columnas.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import pandas as pd
from pandas.api import types as ptypes

log = logging.getLogger(__name__)

ID_REGEX = r"^AGC_\d{3}$"
CONJUNTOS = {"ENTRENAMIENTO", "PREDICCION"}
# Estas columnas pueden ser nulas solo en PREDICCION.
NULOS_SOLO_PREDICCION = {"rendimiento_t_ha", "diag_y_redondo", "diag_y_resolucion"}

# Límites físicos por patrón de nombre: (regex, mínimo, máximo).
# NDVI puede estar entre -1 y 1; el rango 0 a 1 se reporta como advertencia.
RANGOS_DUROS: list[tuple[str, float, float]] = [
    (r"^(pl|s2)_ndvi_(pico|base|max_abr_oct|media_abr_oct)$", -1.0, 1.0),
    (r"_doy$", 1, 366),
    (r"_pct$", 0, 100),
    (r"^soil_ph$", 0, 14),
    (r"^pend_.*_grados$", 0, 90),
    (r"^era5_sm\d", 0, 1),
    (r"^area_ha_geod$", 1e-6, 10_000),
    (r"^rendimiento_t_ha$", 0.1, 15),
]
RANGOS_SUAVES: list[tuple[str, float, float]] = [
    (r"^(pl|s2)_ndvi_(pico|base|max_abr_oct|media_abr_oct)$", 0.0, 1.0),
]
ORDEN_FENOLOGICO = ["pl_sos20_doy", "pl_sos50_doy", "pl_centro_pico_doy", "pl_eos50_doy", "pl_eos20_doy"]


class ContractError(Exception):
    """Indica que el dataset no puede cargarse."""


@dataclass
class Reporte:
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errores


def _familia(dtype) -> str:
    if ptypes.is_bool_dtype(dtype):
        return "bool"
    if ptypes.is_integer_dtype(dtype):
        return "int"
    if ptypes.is_float_dtype(dtype):
        return "float"
    if ptypes.is_string_dtype(dtype) or ptypes.is_object_dtype(dtype):
        return "str"
    return str(dtype)


_FAMILIA_DICC = {"bool": "bool", "boolean": "bool", "int64": "int", "Int64": "int",
                 "float64": "float", "str": "str", "object": "str", "string": "str"}


def validar(df: pd.DataFrame, diccionario: pd.DataFrame, roles: dict[str, list[str]]) -> Reporte:
    r = Reporte()
    dicc = diccionario.set_index("columna")

    # Sin un esquema común, las validaciones posteriores podrían dar resultados engañosos.
    cols_roles = [c for cols in roles.values() for c in cols]
    if len(cols_roles) != len(set(cols_roles)):
        r.errores.append("roles_columnas.json asigna una columna a más de un rol")
    for nombre, esperadas in (("diccionario", set(dicc.index)), ("roles", set(cols_roles))):
        faltan, sobran = esperadas - set(df.columns), set(df.columns) - esperadas
        if faltan:
            r.errores.append(f"Faltan columnas declaradas en {nombre}: {sorted(faltan)}")
        if sobran:
            r.errores.append(f"Columnas no declaradas en {nombre}: {sorted(sobran)}")
    if r.errores:
        return r  # El resto de reglas depende de este esquema.

    # Se valida por familia para aceptar los dtypes equivalentes que usa pandas.
    for col in df.columns:
        esperado = _FAMILIA_DICC.get(dicc.at[col, "tipo"], dicc.at[col, "tipo"])
        real = _familia(df[col].dtype)
        if esperado != real:
            r.errores.append(f"Tipo de '{col}': esperado {esperado}, llegó {real} ({df[col].dtype})")

    # La llave debe ser única y estable para evitar sobrescrituras incorrectas en la carga.
    ids = df["id_poligono"]
    if ids.isna().any():
        r.errores.append("id_poligono contiene nulos")
    if ids.duplicated().any():
        r.errores.append(f"id_poligono duplicados: {ids[ids.duplicated()].tolist()}")
    malos = ids[~ids.astype(str).str.match(ID_REGEX)]
    if len(malos):
        r.errores.append(f"id_poligono fuera de formato {ID_REGEX}: {malos.head().tolist()}")

    # Se separan entrenamiento y predicción para impedir nulos indebidos y fuga del objetivo.
    fuera = set(df["conjunto"].dropna().unique()) - CONJUNTOS
    if fuera or df["conjunto"].isna().any():
        r.errores.append(f"'conjunto' con valores inválidos o nulos: {fuera}")
    entr = df["conjunto"] == "ENTRENAMIENTO"
    for col in NULOS_SOLO_PREDICCION:
        n = int(df.loc[entr, col].isna().sum())
        if n:
            r.errores.append(f"{col}: {n} nulos en ENTRENAMIENTO")
    if df.loc[~entr, "rendimiento_t_ha"].notna().any():
        r.errores.append("rendimiento_t_ha tiene valores en PREDICCION (posible fuga del objetivo)")

    # Los nulos críticos se rechazan aquí; imputarlos pertenece al pipeline de modelado.
    nulos = df.drop(columns=list(NULOS_SOLO_PREDICCION)).isna().sum()
    for col, n in nulos[nulos > 0].items():
        r.errores.append(f"Nulos críticos en '{col}': {n}")

    # Los límites duros protegen la integridad; los suaves señalan datos atípicos sin bloquear.
    for patron, lo, hi, destino in (
        [(p, a, b, r.errores) for p, a, b in RANGOS_DUROS]
        + [(p, a, b, r.advertencias) for p, a, b in RANGOS_SUAVES]
    ):
        for col in (c for c in df.columns if re.search(patron, c)):
            s = df[col].dropna()
            n = int(((s < lo) | (s > hi)).sum())
            if n:
                destino.append(f"'{col}': {n} valores fuera de [{lo}, {hi}] (min={s.min():.4g}, max={s.max():.4g})")

    # Estas reglas detectan combinaciones imposibles aunque cada valor esté dentro de rango.
    textura = df[["soil_arcilla_pct", "soil_arena_pct", "soil_limo_pct"]].sum(axis=1)
    if ((textura - 100).abs() > 1).any():
        r.errores.append("Textura de suelo (arcilla+arena+limo) no suma 100 ± 1 %")
    orden = df[ORDEN_FENOLOGICO]
    rotas = (orden.diff(axis=1).iloc[:, 1:] < 0).any(axis=1)
    if rotas.any():
        r.errores.append(f"Orden fenológico SOS≤pico≤EOS roto en {int(rotas.sum())} parcelas")

    # El drift se reporta para detectar cambios del maestro sin bloquear una carga válida.
    for col in df.select_dtypes("number").columns:
        lo, hi = pd.to_numeric(dicc.at[col, "min"], errors="coerce"), pd.to_numeric(dicc.at[col, "max"], errors="coerce")
        if pd.notna(lo) and pd.notna(hi):
            s = df[col].dropna()
            tol = 1e-9 * max(1.0, abs(hi - lo))
            if s.min() < lo - tol or s.max() > hi + tol:
                r.advertencias.append(f"Drift en '{col}': [{s.min():.4g}, {s.max():.4g}] vs diccionario [{lo:.4g}, {hi:.4g}]")

    # Una feature constante no aporta al modelo, pero no invalida el dataset.
    const = [c for c in roles.get("features", []) if df[c].nunique(dropna=False) <= 1]
    if const:
        r.advertencias.append(f"Features constantes (no aportan al modelo): {const}")

    return r


def exigir(df: pd.DataFrame, diccionario: pd.DataFrame, roles: dict[str, list[str]]) -> Reporte:
    """Valida, registra y lanza ContractError si hay errores."""
    rep = validar(df, diccionario, roles)
    for w in rep.advertencias:
        log.warning("Contrato | %s", w)
    for e in rep.errores:
        log.error("Contrato | %s", e)
    if not rep.ok:
        raise ContractError(f"{len(rep.errores)} violaciones de contrato; carga cancelada.")
    log.info("Contrato OK | %d advertencias", len(rep.advertencias))
    return rep
