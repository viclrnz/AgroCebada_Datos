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

## modelado/ : selección de variables, modelos y predicciones (Edgardo)

| Orden | Notebook | Qué hace | Lee | Escribe |
|---|---|---|---|---|
| 0 | `00_random_forest_base.ipynb` | Línea base y comparación: Random Forest con 51 variables, selección por SHAP (12 variables), torneo de algoritmos y SVR de 12 variables (modelo anterior, superado por el ensamble de 16). Lee `dataset_greedy.csv`. Sus conclusiones del bonus quedan superadas por 02. | `dataset_greedy.csv` | `dataset_comparacion_rendimientos.csv`, `dataset_rendimientos_estimados.csv` |
| 1 | `01_preprocesamiento.ipynb` | Lee `matriz_caracteristicas` de Supabase (credenciales del `.env`), quita 11 variables redundantes, deja 51 predictoras y crea `grupo_rend` (KMeans de 2 grupos sobre el rendimiento) para estratificar la validación cruzada. | Supabase | `dataset_modelo.csv` (197 x 58) |
| 2 | `02_modelado_ensamble_svr.ipynb` | Validación cruzada estratificada de 5 pliegues. Compara Random Forest con importancia por permutación (19 variables), Random Forest con GridSearchCV, el ensamble RF + SVR y la selección hacia atrás (SBE), que deja 16 variables. Predice las 59 parcelas, grafica el diagnóstico y responde las preguntas bonus. | `dataset_modelo.csv`, `dataset_62vars.csv` | `comparacion_rendimientos.csv`, `dataset_rendimientos_estimados.csv`, `Diagnostico_Final_Ensamble_16vars.png` |

Notas:
- El modelo final es el ensamble de 16 variables (0.16 Random Forest + 0.84 SVR): en validación cruzada R² 0.672, MAE 0.374 t/ha y RMSE 0.486 t/ha. En `comparacion_rendimientos.csv` es la columna `M6_Ensamble_Final_SBE_16vars`.
- Las salidas del paso 2 se copian a `data/predictions/` (`comparacion_modelos_rendimiento.csv` y `rendimientos_estimados.csv`). Luego `python main.py rendimientos` las carga a Supabase para la app.
- `dataset_62vars.csv` trae las 62 variables originales para reproducir el modelo base (M1).
- Necesita `python-dotenv` y un `.env` con `DB_USER`, `DB_PASSWORD` y `DB_HOST` (ver `.env.example`).
