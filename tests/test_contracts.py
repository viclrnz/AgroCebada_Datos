"""Pruebas del contrato de datos. Ejecutar con `pytest -q`."""
import pandas as pd
import pytest

from config import settings
from src.contracts import validar
from src.extract import extract
from src.load import _dividir_sentencias
from src.transform import normalizar_tipos


@pytest.fixture(scope="module")
def insumos():
    return extract()


@pytest.fixture
def df(insumos):
    return normalizar_tipos(insumos.maestro, insumos.diccionario)


def _errores(df, ins):
    return validar(df, ins.diccionario, ins.roles).errores


def test_maestro_entregado_cumple_contrato(df, insumos):
    assert _errores(df, insumos) == []


def test_csv_equivale_al_parquet(df, insumos):
    csv = normalizar_tipos(pd.read_csv(settings.RAW_DIR / "maestro_agrocebada.csv"), insumos.diccionario)
    pd.testing.assert_frame_equal(df, csv, check_exact=False, rtol=1e-12)


def test_id_duplicado(df, insumos):
    df.loc[1, "id_poligono"] = df.loc[0, "id_poligono"]
    assert any("duplicados" in e for e in _errores(df, insumos))


def test_ndvi_fuera_de_rango_fisico(df, insumos):
    df.loc[0, "pl_ndvi_pico"] = 1.3
    assert any("pl_ndvi_pico" in e for e in _errores(df, insumos))


def test_objetivo_nulo_en_entrenamiento(df, insumos):
    i = df.index[df["conjunto"] == "ENTRENAMIENTO"][0]
    df.loc[i, "rendimiento_t_ha"] = None
    assert any("rendimiento_t_ha" in e for e in _errores(df, insumos))


def test_fuga_objetivo_en_prediccion(df, insumos):
    i = df.index[df["conjunto"] == "PREDICCION"][0]
    df.loc[i, "rendimiento_t_ha"] = 4.0
    assert any("fuga" in e for e in _errores(df, insumos))


def test_nulo_critico_en_feature(df, insumos):
    df.loc[0, "soil_ph"] = None
    assert any("soil_ph" in e for e in _errores(df, insumos))


def test_columna_faltante(df, insumos):
    assert any("Faltan columnas" in e for e in _errores(df.drop(columns="soil_ph"), insumos))


def test_orden_fenologico(df, insumos):
    df.loc[0, "pl_sos50_doy"] = df.loc[0, "pl_eos20_doy"] + 1
    assert any("fenológico" in e for e in _errores(df, insumos))


def test_divisor_sql_respeta_bloques_dolar():
    sql = "DO $$ BEGIN RAISE NOTICE 'a;b'; END $$;\n-- comentario; con punto y coma\nSELECT 1;"
    assert _dividir_sentencias(sql) == ["DO $$ BEGIN RAISE NOTICE 'a;b'; END $$", "SELECT 1"]
