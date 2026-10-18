"""Pruebas del shapefile de parcelas. Ejecutar con `pytest -q`."""
import pytest
import shapefile
from shapely.geometry import Point, shape

from config import settings
from src.contracts import ContractError
from src.extract import extract
from src.parcelas import leer_parcelas
from src.rendimientos import validar_parcelas


@pytest.fixture(scope="module")
def maestro():
    return extract().maestro


@pytest.fixture
def parcelas():
    return leer_parcelas()


def test_shapefile_entregado_cumple_contrato(parcelas, maestro):
    validar_parcelas(parcelas, maestro)


def test_marcador_dentro_de_cada_parcela(parcelas):
    with shapefile.Reader(str(settings.PARCELAS_PATH), encoding="utf-8") as r:
        geoms = {sr.record["ID_POLIGON"]: shape(sr.shape.__geo_interface__) for sr in r.iterShapeRecords()}
    fuera = [p.id_poligono for p in parcelas.itertuples()
             if not geoms[p.id_poligono].contains(Point(p.longitud, p.latitud))]
    assert fuera == []


def test_parcela_faltante(parcelas, maestro):
    with pytest.raises(ContractError):
        validar_parcelas(parcelas.iloc[1:], maestro)


def test_municipio_distinto(parcelas, maestro):
    parcelas.loc[0, "municipio"] = "Otro"
    with pytest.raises(ContractError):
        validar_parcelas(parcelas, maestro)


def test_coordenadas_invertidas(parcelas, maestro):
    parcelas.loc[0, ["latitud", "longitud"]] = parcelas.loc[0, ["longitud", "latitud"]].values
    with pytest.raises(ContractError):
        validar_parcelas(parcelas, maestro)
