# Notebooks

Organizados por etapa del proyecto. Se ejecutan en este orden.

## etl/ : construcción de la matriz de características (Dana)

Generan `maestro_agrocebada.parquet/.csv`, `diccionario_variables.csv` y `roles_columnas.json`, que se copian a `data/raw/`. A partir de ahí `python main.py run` los valida y los carga a Supabase.

| Orden | Notebook | Qué hace | Lee | Escribe (en `data/interim/`) |
|---|---|---|---|---|
| 1 | `01_base_limpia.ipynb` | Estandariza columnas, limpia las series de Sentinel-2, Landsat y Planet, cruza el shapefile con el CSV de rendimiento y extrae topografía (INEGI CEM) y clima mensual (CHIRPS, CHIRTS) por parcela. | Datos oficiales del reto (`DIR_DATOS`) | `parcelas_base`, `s2_limpio`, `ls_limpio`, `pl_limpio`, `topo_parcela`, `clima_mensual_parcela`, `gradiente_termico.csv` |
| 2 | `02_fenologia.ipynb` (hasta la celda que guarda `fenologia_parcela`) | Suaviza las curvas de NDVI y LAI (Whittaker) y calcula la fenología por parcela: inicio y fin de temporada, pico e integrales. | Salidas del paso 1 | `fenologia_parcela`, `curvas_diarias_pl` |
| 3 | `03_externas.ipynb` | Descarga con Google Earth Engine: CHIRPS diario (lluvia, balance hídrico, grados día), SoilGrids 2.0 (arcilla, pH y otras, 0 a 30 cm) y ERA5-Land diario (déficit de presión de vapor, humedad del suelo). | Salidas de 1 y 2, y Earth Engine | `agroclima_parcela`, `soil_parcela`, `era5_parcela` |
| 4 | `02_fenologia.ipynb` (últimas celdas) | Ensambla el maestro (parcelas, topografía, fenología, agroclima, suelo y ERA5), revisa contratos y guarda la matriz final. | Todas las tablas de `data/interim/` | `data/processed/maestro_agrocebada.*`, `diccionario_variables.csv`, `roles_columnas.json` |

Notas:
- El ensamble final está al final de `02_fenologia.ipynb`, pero necesita las tablas de `03_externas.ipynb`; por eso el paso 4 va después del 3.
- Antes de correr, cambia `DIR_DATOS` en `01_base_limpia.ipynb` a la carpeta donde tengas los datos del reto.
- `03_externas.ipynb` necesita una cuenta de Google Earth Engine (`ee.Authenticate()`) y un proyecto propio en `PROYECTO_EE`.
- Verificado (2026-10-19): el ensamble produce (197, 95) con 62 variables de entrada, igual que `data/raw/maestro_agrocebada.parquet` y `roles_columnas.json` de este repo.

## eda/ : análisis exploratorio

| Notebook | Qué hace |
|---|---|
| `01_eda.ipynb` | Análisis exploratorio de la matriz de características. |

## modelado/ : entrenamiento y comparación de modelos (Edgardo)

| Notebook | Qué hace |
|---|---|
| `02_preprocesamiento_rf.ipynb` | Preprocesamiento y primeras pruebas con Random Forest. |
| (pendiente) | Notebooks de Edgardo con la selección de variables y el ensamble final de 16 variables (M6). |
