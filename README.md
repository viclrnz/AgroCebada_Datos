# AgroCebada_Datos

ETL y datos del Reto AgroCebada 2026 (FIRA), equipo SocieData. El repositorio arma la matriz de características de 197 parcelas de cebada, la valida y la carga a PostgreSQL en Supabase, que es la base que usa la app web.

De las 197 parcelas, 138 tienen rendimiento conocido y se usan para entrenar. Para las otras 59 el rendimiento se estima con el modelo final.

## Flujo

1. Los notebooks de `notebooks/etl/` generan el maestro (`data/raw/maestro_agrocebada.parquet`), el diccionario de variables y los roles de columnas.
2. `python main.py run` valida el maestro contra un contrato de datos y lo carga a la tabla `matriz_caracteristicas`.
3. Los notebooks de `notebooks/modelado/` entrenan los modelos y dejan las predicciones en `data/predictions/`.
4. `python main.py rendimientos` toma las predicciones del modelo elegido, agrega ubicación y superficie desde el shapefile y las carga a `rendimientos_estimados`, que es lo que lee la app.

## Estructura del repositorio

| Carpeta | Qué contiene |
|---|---|
| `main.py` | Punto de entrada del ETL (comandos abajo) |
| `config/` | Rutas, variables de entorno, conexión a la base y logs |
| `src/` | Código del ETL: extracción, contrato de datos, transformación, carga, rendimientos y parcelas |
| `sql/` | Migraciones de la base (tablas, vistas y rol del chatbot), en orden `001` a `007` |
| `tests/` | Pruebas con pytest |
| `data/raw/` | Maestro, diccionario de variables, roles de columnas y shapefile de parcelas |
| `data/predictions/` | Predicciones de los modelos M1 a M6 |
| `notebooks/` | Notebooks por etapa: etl, eda y modelado |
| `docs/` | Auditoría del maestro y explicación de por qué no hay `.pkl` |
| `logs/` | Log del ETL (`etl.log`) |

## Cómo ejecutarlo

Probado en Windows con Miniconda.

```bash
conda activate agrocebada_env
pip install -r requirements.txt
copy .env.example .env
```

En `.env` hay que llenar las credenciales de Supabase: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` y `DB_SSL`. También trae `ETL_TABLA_DESTINO`, `ETL_ESQUEMA_DESTINO` y `ETL_CHUNK_SIZE`. Opcionalmente, `ETL_MODELO_VIGENTE` cambia el modelo que se carga (por defecto `ensamble_16vars`).

Comandos:

```bash
pytest -q                        # 23 pruebas
python main.py validar           # revisa el maestro contra el contrato, sin tocar la base
python main.py init-db           # crea tablas y vistas (una vez, o si cambia sql/)
python main.py run               # carga el maestro a matriz_caracteristicas
python main.py rendimientos      # carga los rendimientos del modelo vigente
python main.py rendimientos --modelo svr_19vars   # carga otro modelo
```

Códigos de salida: `0` correcto, `1` error inesperado, `2` el contrato falló y no se cargó nada.

La carga es idempotente: si se corre dos veces con el mismo maestro, la segunda no cambia filas. Cada ejecución queda registrada en la tabla `etl_ejecuciones`.

## Modelo final

Métricas de validación cruzada sobre las 138 parcelas con rendimiento conocido (RMSE y MAE en t/ha):

| Modelo | `--modelo` | RMSE | MAE | R² |
|---|---|---|---|---|
| M1 Random Forest, 62 variables | `rf_62vars` | 0.575 | 0.433 | 0.541 |
| M2 Random Forest, 19 variables | `rf_19vars` | 0.546 | 0.416 | 0.586 |
| M3 Random Forest con GridSearch, 19 variables | `rf_gridsearch_19vars` | 0.536 | 0.401 | 0.601 |
| M4 SVR RBF, 19 variables | `svr_19vars` | 0.510 | 0.390 | 0.638 |
| M5 Ensamble, 19 variables | `ensamble_19vars` | 0.506 | 0.386 | 0.644 |
| M6 Ensamble, 16 variables (usado) | `ensamble_16vars` | 0.486 | 0.374 | 0.672 |

El modelo usado es M6: 0.16 Random Forest + 0.84 SVR con 16 variables elegidas por selección hacia atrás.

No se exportó el modelo entrenado (`.pkl`). La app no hace inferencia, solo lee las predicciones ya cargadas. Los detalles están en `docs/modelo_sin_pkl.md`.

## Más información

- Orden y descripción de los notebooks: [notebooks/README.md](notebooks/README.md)
- Auditoría del maestro: [docs/auditoria_maestro_2026-10-11.md](docs/auditoria_maestro_2026-10-11.md)
- Predicciones sin `.pkl` y lista de modelos: [docs/modelo_sin_pkl.md](docs/modelo_sin_pkl.md)
