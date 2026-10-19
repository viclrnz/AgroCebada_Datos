# Notebooks

Están separados por etapa y se corren en el orden de las tablas.

## etl/ : matriz de características

Las tablas intermedias se guardan en `data/interim/`. El resultado final se copia a `data/raw/` y de ahí lo carga `python main.py run`.

| Orden | Notebook | Qué hace | Lee | Escribe |
|---|---|---|---|---|
| 1 | `01_base_limpia.ipynb` | Limpia las series de Sentinel-2, Landsat y Planet, cruza el shapefile con el rendimiento y saca topografía (INEGI CEM) y clima mensual (CHIRPS, CHIRTS) por parcela. | Datos oficiales del reto (`DIR_DATOS`) | `parcelas_base`, `s2_limpio`, `ls_limpio`, `pl_limpio`, `topo_parcela`, `clima_mensual_parcela`, `gradiente_termico.csv` |
| 2 | `02_fenologia.ipynb` (hasta la celda que guarda `fenologia_parcela`) | Suaviza NDVI y LAI (Whittaker) y calcula la fenología: inicio y fin de temporada, pico e integrales. | Salidas del paso 1 | `fenologia_parcela`, `curvas_diarias_pl` |
| 3 | `03_externas.ipynb` | Descarga de Google Earth Engine CHIRPS diario, SoilGrids 2.0 (0 a 30 cm) y ERA5-Land diario. | Salidas de 1 y 2, Earth Engine | `agroclima_parcela`, `soil_parcela`, `era5_parcela` |
| 4 | `02_fenologia.ipynb` (últimas celdas) | Une todas las tablas, revisa contratos y guarda la matriz final. | Tablas de `data/interim/` | `data/processed/maestro_agrocebada.*`, `diccionario_variables.csv`, `roles_columnas.json` |

Notas:
- El paso 4 está al final de `02_fenologia.ipynb` pero necesita las tablas de `03_externas.ipynb`, por eso va después del 3.
- Antes de correr, cambia `DIR_DATOS` en `01_base_limpia.ipynb` a la carpeta con los datos del reto.
- `03_externas.ipynb` pide una cuenta de Google Earth Engine (`ee.Authenticate()`) y un proyecto propio en `PROYECTO_EE`.
- Verificado el 2026-10-19: el ensamble da (197, 95) con 62 variables de entrada, igual que `data/raw/maestro_agrocebada.parquet` y `roles_columnas.json`.

## eda/ : análisis exploratorio

| Notebook | Qué hace |
|---|---|
| `01_eda.ipynb` | Análisis exploratorio de la matriz de características. |

## modelado/ : modelos y predicciones

| Orden | Notebook | Qué hace | Lee | Escribe |
|---|---|---|---|---|
| 0 | `00_random_forest_base.ipynb` | Línea base: Random Forest con 51 variables, selección por SHAP (12 variables), comparación de algoritmos y SVR de 12 variables. | `dataset_greedy.csv` | `dataset_comparacion_rendimientos.csv`, `dataset_rendimientos_estimados_svr12.csv` |
| 1 | `01_preprocesamiento.ipynb` | Lee `matriz_caracteristicas` de Supabase, quita 11 variables redundantes (quedan 51) y crea `grupo_rend` (KMeans de 2 grupos) para estratificar la validación cruzada. | Supabase | `dataset_modelo.csv` (197 x 58) |
| 2 | `02_modelado_ensamble_svr.ipynb` | Validación cruzada estratificada de 5 pliegues. Compara Random Forest (19 variables), Random Forest con GridSearchCV, ensamble RF + SVR y selección hacia atrás, que deja 16 variables. Predice las 59 parcelas y responde las preguntas bonus. | `dataset_modelo.csv`, `dataset_62vars.csv` | `comparacion_rendimientos.csv`, `dataset_rendimientos_estimados.csv`, `Diagnostico_Final_Ensamble_16vars.png` |

Notas:
- `00_random_forest_base.ipynb` queda como evidencia de la comparación anterior. Su SVR de 12 variables fue superado por el ensamble de 16 y sus respuestas bonus las reemplaza el notebook 02.
- El modelo final es el Modelo 5: Ensamble Final tras selección de variables SBE (16 variables predictoras), 0.16 Random Forest + 0.84 SVR. En `comparacion_rendimientos.csv` es la columna `M6_Ensamble_Final_SBE_16vars`. Las métricas están en el [README principal](../README.md#modelo-final).
- Las salidas del paso 2 se copian a `data/predictions/` como `comparacion_modelos_rendimiento.csv` y `rendimientos_estimados.csv`. Luego `python main.py rendimientos` las carga a Supabase.
- `dataset_62vars.csv` trae las 62 variables originales para reproducir el Modelo base (Random Forest Original, 62 variables).
- El notebook 01 necesita `python-dotenv` y un `.env` con `DB_USER`, `DB_PASSWORD` y `DB_HOST` (ver `.env.example`).
