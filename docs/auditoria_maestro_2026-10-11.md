# Auditoría del Dataset Maestro — 11/10/2026

Insumo: `maestro_agrocebada.parquet` (SHA-256 `a1ac0c7b060d…`), 197 parcelas × 95 columnas.

## Resultado: APTO para carga

| Verificación | Resultado |
|---|---|
| Parquet y CSV: mismas columnas, orden y valores | ✔ (diferencia numérica máxima 4.5e-13) |
| Columnas = diccionario = roles (95) sin duplicados de rol | ✔ |
| Rol por columna, diccionario vs. JSON | ✔ coinciden |
| `id_poligono` único, sin nulos, formato `AGC_###` | ✔ |
| Conjuntos | 138 ENTRENAMIENTO / 59 PREDICCION |
| `rendimiento_t_ha` | sin nulos en ENTRENAMIENTO; todo nulo en PREDICCION |
| Nulos en otras columnas | 0 (solo `diag_y_redondo` y `diag_y_resolucion`, ligados al objetivo) |
| Filas duplicadas | 0 |
| Rangos vs. diccionario | ✔ coinciden exactamente |
| NDVI (pico, base, máx., media) | dentro de [0.17, 0.89] |
| Textura del suelo (arcilla + arena + limo) | 100 % en todas las parcelas |
| Orden fenológico Planet SOS20 ≤ SOS50 ≤ pico ≤ EOS50 ≤ EOS20 | ✔ en las 197 |

## Observaciones para Preprocesamiento (no bloquean)

1. **Unidades erróneas en el diccionario**: `rendimiento_t_ha` dice "ha" (debe ser t/ha) y
   `area_ha_geod` dice "adimensional" (debe ser ha). Hay variables en días o °C·día marcadas
   como "adimensional / índice" (`pl_dias_meseta`, `ac_racha_seca_*`, `ac_gdd_*`).
2. **Columnas constantes**: `diag_sin_ciclo`, `diag_s2_sin_ciclo` (todo False) y los cuatro
   `era5_dias_tmax28/30_*` (todo 0). Están en diagnóstico o podadas, así que no afectan al modelo.
3. **Redundancia ya resuelta por la poda**: `pl_ndvi_max_abr_oct` es idéntica a `pl_ndvi_pico`
   (r = 1.0) y `pl_ndvi_media_abr_oct` es proporcional a `pl_ndvi_int_abr_oct` (r = 1.0).

## Observaciones para Modelado

- `ndvi_int_*` y `*_integral_ciclo` son integrales (valores de 18 a 127), no NDVI; no se les aplica el rango [0, 1].
- Hay 25 `clima_pixel_id` distintos para 197 parcelas, y uno solo agrupa 51. Las parcelas de un
  mismo píxel reciben el mismo forzamiento climático (sus valores `era5_*`/`ac_*` difieren porque
  las ventanas fenológicas cambian por parcela), lo que genera correlación espacial. Conviene
  validar también con `GroupKFold` por `clima_pixel_id` para no inflar la métrica.
- 45 de los 138 rendimientos están redondeados (`diag_y_redondo`) con resolución de hasta 0.5 t/ha;
  eso marca un piso de error irreducible para el RMSE.
