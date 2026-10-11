# AgroCebada_Datos

Pipeline ETL del **Proyecto AgroCebada 2026** (FIRA, equipo SocieData). Toma el Dataset Maestro
de Preprocesamiento, lo valida contra un contrato de datos y lo carga de forma idempotente
a Supabase (PostgreSQL), que es la fuente única de la verdad para Modelado y para la app Django.

```
data/raw/ (entregable de Dana)
   │  extract   → lee Parquet + diccionario + roles, calcula SHA-256
   │  contrato  → esquema, tipos, llave, nulos, rangos físicos, coherencia agronómica
   │  transform → tipos estables + metadatos de linaje (run_id, fecha, sha256)
   ▼  load      → UPSERT por chunks en una sola transacción + bitácora
Supabase: matriz_caracteristicas · etl_ejecuciones · v_parcelas_app
```

## Estructura

| Ruta | Contenido |
|---|---|
| `config/settings.py` | Rutas, variables de entorno y engine SQLAlchemy (`pg8000` + SSL) |
| `config/logging_config.py` | Logs a consola y a `logs/etl.log` (rotativo) |
| `src/extract.py` | Lectura de insumos y huella SHA-256 |
| `src/contracts.py` | Contrato de datos (ERROR detiene la carga, WARNING solo avisa) |
| `src/transform.py` | Normalización de tipos y linaje; **no** imputa ni escala |
| `src/schema.py` | Genera el DDL desde `diccionario_variables.csv` |
| `src/load.py` | Migraciones, upsert idempotente y bitácora |
| `sql/` | Migraciones idempotentes, ejecutadas en orden |
| `tests/` | Pruebas del contrato (`pytest -q`) |
| `data/raw/` | Entregables versionados de Preprocesamiento |
| `notebooks/` | Notebooks de Dana (trazabilidad del maestro) |

## Puesta en marcha (Windows + Miniconda)

```bash
conda activate agrocebada_env
pip install -r requirements.txt
copy .env.example .env          # y completa DB_PASSWORD, DB_USER, DB_HOST
pytest -q                       # 10 pruebas en verde
python main.py validar          # contrato sin tocar la BD
python main.py init-db          # crea tablas, bitácora y vista (una vez, o tras cambiar sql/)
python main.py run              # carga
```

Códigos de salida: `0` OK, `1` error inesperado, `2` contrato violado (no se cargó nada).

## Decisiones de diseño

- **Parquet como fuente canónica.** El CSV pierde el tipo `boolean` con nulos (`diag_y_redondo`).
  El pipeline acepta ambos y re-tipifica según el diccionario.
- **Idempotencia real.** `ON CONFLICT (id_poligono) DO UPDATE ... WHERE (...) IS DISTINCT FROM (...)`:
  si se ejecuta dos veces con el mismo maestro, la segunda reporta 0 filas afectadas y
  conserva la fecha de carga original.
- **Atomicidad.** Todos los chunks van en una transacción; ante cualquier error hay rollback completo.
- **Migración desde la PoC.** `sql/001` renombra la tabla creada con `to_sql(replace)` (sin PK)
  a `matriz_caracteristicas_poc_respaldo`; `sql/002` la recrea con PK y CHECKs.
- **Sin borrado silencioso.** Si en la BD hay parcelas que ya no vienen en el maestro, se reportan en el log.
- **Sin lógica de modelado en el ETL.** La imputación, el escalado y la selección de variables viven en el
  `Pipeline` de sklearn de Modelado, para evitar fuga entre ENTRENAMIENTO y PREDICCION.
- **Contrato estable para Django.** La app consume `v_parcelas_app` (modelo `managed = False`),
  no la tabla, para que un cambio de esquema no rompa la web.

## Si cambia el diccionario de variables

```bash
python -m src.schema > sql/002_matriz_caracteristicas.sql
```

`CREATE TABLE IF NOT EXISTS` no altera una tabla existente: agregar o quitar columnas
requiere una migración nueva (`sql/005_...sql` con `ALTER TABLE`).
