"""
Prepara la tabla de rendimientos que muestra la app.

Modelado no exporta un `.pkl`; entrega `comparacion_modelos_rendimiento.csv`
con las predicciones de cada modelo. Aquí se elige el modelo vigente: las
parcelas de ENTRENAMIENTO conservan su rendimiento observado y las de
PREDICCION toman el valor del modelo. La tabla también lleva los datos que
muestra la app (estado, municipio, superficie y coordenadas) para que el Front
la lea sin joins. Antes de cargar se comprueba que el archivo de predicciones y
el shapefile coincidan 1 a 1 con el maestro.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import pandas as pd

from src.contracts import ContractError

log = logging.getLogger(__name__)

# Nombre corto del modelo -> columna en el archivo de comparación.
MODELOS = {
    "svr_12vars": "rendimiento_pred_svr_12vars",
    "rf_12vars": "rendimiento_pred_rf_12vars",
    "rf_50vars": "rendimiento_pred_50vars",
}
DECIMALES = 2
COLUMNAS = ["id_poligono", "estado", "municipio", "conjunto", "superficie_ha", "latitud", "longitud",
            "rendimiento_estimado_t_ha", "origen", "modelo"]
# Caja que cubre Hidalgo, Puebla y Tlaxcala; detecta coordenadas invertidas o en otra proyección.
LAT_RANGO, LON_RANGO = (18.0, 21.5), (-99.5, -97.0)
TOLERANCIA_AREA_HA = 0.05


def validar_comparacion(comparacion: pd.DataFrame, maestro: pd.DataFrame, modelo: str) -> None:
    """Detiene la carga si el archivo no corresponde 1 a 1 con el maestro."""
    if modelo not in MODELOS:
        raise ContractError(f"Modelo desconocido '{modelo}'. Opciones: {sorted(MODELOS)}")
    col = MODELOS[modelo]
    errores = []

    faltan = {"id_poligono", "conjunto", "rendimiento_t_ha", col} - set(comparacion.columns)
    if faltan:
        raise ContractError(f"Faltan columnas en el archivo de comparación: {sorted(faltan)}")

    dup = comparacion["id_poligono"][comparacion["id_poligono"].duplicated()]
    if not dup.empty:
        errores.append(f"id_poligono duplicados: {sorted(dup)[:10]}")

    # outer + indicator muestra parcelas que sobran o faltan en cualquiera de los lados.
    cruce = comparacion.merge(
        maestro[["id_poligono", "conjunto", "rendimiento_t_ha"]],
        on="id_poligono", how="outer", suffixes=("", "_maestro"), indicator=True,
    )
    solo_archivo = cruce.loc[cruce["_merge"] == "left_only", "id_poligono"]
    solo_maestro = cruce.loc[cruce["_merge"] == "right_only", "id_poligono"]
    if not solo_archivo.empty:
        errores.append(f"{len(solo_archivo)} parcelas no existen en el maestro: {sorted(solo_archivo)[:10]}")
    if not solo_maestro.empty:
        errores.append(f"{len(solo_maestro)} parcelas del maestro no tienen rendimiento: {sorted(solo_maestro)[:10]}")

    ambos = cruce[cruce["_merge"] == "both"]
    distinto = ambos.loc[ambos["conjunto"] != ambos["conjunto_maestro"], "id_poligono"]
    if not distinto.empty:
        errores.append(f"conjunto distinto al del maestro en: {sorted(distinto)[:10]}")

    # El observado debe ser el mismo que está en Supabase.
    obs = ambos[ambos["conjunto"] == "ENTRENAMIENTO"]
    difiere = obs.loc[(obs["rendimiento_t_ha"] - obs["rendimiento_t_ha_maestro"]).abs() > 1e-6, "id_poligono"]
    if not difiere.empty:
        errores.append(f"rendimiento observado distinto al del maestro en: {sorted(difiere)[:10]}")

    pred = comparacion[comparacion["conjunto"] == "PREDICCION"]
    if pred[col].isna().any():
        errores.append(f"{int(pred[col].isna().sum())} parcelas de PREDICCION sin valor en {col}")

    if errores:
        for e in errores:
            log.error("Rendimientos | %s", e)
        raise ContractError(f"El archivo de rendimientos no cumple el contrato ({len(errores)} errores)")


def validar_parcelas(parcelas: pd.DataFrame, maestro: pd.DataFrame) -> None:
    """Detiene la carga si el shapefile no corresponde 1 a 1 con el maestro."""
    errores = []
    dup = parcelas["id_poligono"][parcelas["id_poligono"].duplicated()]
    if not dup.empty:
        errores.append(f"id_poligono duplicados en el shapefile: {sorted(dup)[:10]}")

    cruce = parcelas.merge(maestro[["id_poligono", "estado", "municipio", "conjunto", "area_ha_geod"]],
                           on="id_poligono", how="outer", suffixes=("", "_maestro"), indicator=True)
    for lado, texto in (("left_only", "no existen en el maestro"), ("right_only", "del maestro no están en el shapefile")):
        ids = cruce.loc[cruce["_merge"] == lado, "id_poligono"]
        if not ids.empty:
            errores.append(f"{len(ids)} parcelas {texto}: {sorted(ids)[:10]}")

    ambos = cruce[cruce["_merge"] == "both"]
    for col in ("estado", "municipio", "conjunto"):
        dif = ambos.loc[ambos[col] != ambos[f"{col}_maestro"], "id_poligono"]
        if not dif.empty:
            errores.append(f"{col} distinto al del maestro en: {sorted(dif)[:10]}")
    dif = ambos.loc[(ambos["area_ha_shp"] - ambos["area_ha_geod"]).abs() > TOLERANCIA_AREA_HA, "id_poligono"]
    if not dif.empty:
        errores.append(f"superficie difiere más de {TOLERANCIA_AREA_HA} ha en: {sorted(dif)[:10]}")

    fuera = parcelas.loc[~parcelas["latitud"].between(*LAT_RANGO) | ~parcelas["longitud"].between(*LON_RANGO),
                         "id_poligono"]
    if not fuera.empty:
        errores.append(f"coordenadas fuera de la zona de estudio en: {sorted(fuera)[:10]}")

    if errores:
        for e in errores:
            log.error("Parcelas | %s", e)
        raise ContractError(f"El shapefile de parcelas no cumple el contrato ({len(errores)} errores)")


def preparar_rendimientos(comparacion: pd.DataFrame, maestro: pd.DataFrame, parcelas: pd.DataFrame,
                          modelo: str, fuente_sha256: str) -> tuple[pd.DataFrame, str]:
    """Arma la tabla final con una sola columna de rendimiento, su origen y la ubicación."""
    es_obs = comparacion["conjunto"] == "ENTRENAMIENTO"
    out = pd.DataFrame({
        "id_poligono": comparacion["id_poligono"].astype("string").str.strip(),
        "rendimiento_estimado_t_ha": comparacion["rendimiento_t_ha"]
            .where(es_obs, comparacion[MODELOS[modelo]]).round(DECIMALES),
        "origen": es_obs.map({True: "observado", False: "modelo"}).astype("string"),
        "modelo": pd.Series(pd.NA, index=comparacion.index, dtype="string").where(es_obs, modelo),
    })

    # Atributos desde el maestro (fuente única) y solo las coordenadas desde el shapefile.
    atributos = maestro[["id_poligono", "estado", "municipio", "conjunto", "area_ha_geod"]] \
        .rename(columns={"area_ha_geod": "superficie_ha"}).astype({"id_poligono": "string"})
    coords = parcelas[["id_poligono", "latitud", "longitud"]].astype({"id_poligono": "string"})
    out = (out.merge(atributos, on="id_poligono", how="left", validate="one_to_one")
              .merge(coords, on="id_poligono", how="left", validate="one_to_one"))
    if out[COLUMNAS].isna().drop(columns="modelo").any().any():
        raise ContractError("Quedaron nulos tras el cruce con maestro y shapefile")
    # 6 decimales en coordenadas equivalen a ~0.1 m; más precisión no aporta en un mapa.
    out = out.round({"superficie_ha": DECIMALES, "latitud": 6, "longitud": 6})
    out = out[COLUMNAS].sort_values("id_poligono").reset_index(drop=True)

    run_id = str(uuid.uuid4())
    out["etl_run_id"] = run_id
    out["etl_cargado_en"] = datetime.now(timezone.utc)
    out["etl_fuente_sha256"] = fuente_sha256

    log.info(
        "Rendimientos OK | %d filas | observado=%d | %s=%d | run_id=%s",
        len(out), int(es_obs.sum()), modelo, int((~es_obs).sum()), run_id,
    )
    return out, run_id
