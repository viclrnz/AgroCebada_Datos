"""Pruebas de la tabla de rendimientos estimados. Ejecutar con `pytest -q`."""
import pandas as pd
import pytest

from config import settings
from src.contracts import ContractError
from src.extract import extract
from src.parcelas import leer_parcelas
from src.rendimientos import leer_comparacion, preparar_rendimientos, validar_comparacion


@pytest.fixture(scope="module")
def maestro():
    return extract().maestro


@pytest.fixture(scope="module")
def parcelas():
    return leer_parcelas()


@pytest.fixture
def comparacion():
    return leer_comparacion(settings.COMPARACION_PATH)


def test_archivo_entregado_cumple_contrato(comparacion, maestro):
    validar_comparacion(comparacion, maestro, "ensamble_16vars")


def test_tabla_final(comparacion, maestro, parcelas):
    df, _ = preparar_rendimientos(comparacion, maestro, parcelas, "ensamble_16vars", "0" * 64)
    assert len(df) == len(comparacion) and df["id_poligono"].is_unique
    assert df.drop(columns="modelo").notna().all().all()
    assert (df["rendimiento_estimado_t_ha"].round(2) == df["rendimiento_estimado_t_ha"]).all()
    obs = df["origen"] == "observado"
    assert df.loc[obs, "modelo"].isna().all()
    assert (df.loc[~obs, "modelo"] == "ensamble_16vars").all()


def test_coincide_con_rendimientos_estimados_csv(comparacion, maestro, parcelas):
    # El CSV entregado por Modelado usa el ensamble final de 16 variables.
    df, _ = preparar_rendimientos(comparacion, maestro, parcelas, "ensamble_16vars", "0" * 64)
    ref = pd.read_csv(settings.PREDICTIONS_DIR / "rendimientos_estimados.csv").sort_values("id_poligono")
    pd.testing.assert_series_equal(
        df["rendimiento_estimado_t_ha"].reset_index(drop=True),
        ref["rendimiento_t_ha"].round(2).reset_index(drop=True),
        check_names=False,
    )


def test_cambio_de_modelo(comparacion, maestro, parcelas):
    df, _ = preparar_rendimientos(comparacion, maestro, parcelas, "svr_19vars", "0" * 64)
    assert set(df["modelo"].dropna()) == {"svr_19vars"}


def test_modelo_desconocido(comparacion, maestro):
    with pytest.raises(ContractError):
        validar_comparacion(comparacion, maestro, "xgboost")


def test_parcela_faltante(comparacion, maestro):
    with pytest.raises(ContractError):
        validar_comparacion(comparacion.iloc[1:], maestro, "ensamble_16vars")


def test_observado_distinto_al_maestro(comparacion, maestro):
    i = comparacion.index[comparacion["conjunto"] == "ENTRENAMIENTO"][0]
    comparacion.loc[i, "rendimiento_t_ha"] += 1
    with pytest.raises(ContractError):
        validar_comparacion(comparacion, maestro, "ensamble_16vars")


def test_prediccion_sin_valor(comparacion, maestro):
    i = comparacion.index[comparacion["conjunto"] == "PREDICCION"][0]
    comparacion.loc[i, "m6_ensamble_final_sbe_16vars"] = None
    with pytest.raises(ContractError):
        validar_comparacion(comparacion, maestro, "ensamble_16vars")
