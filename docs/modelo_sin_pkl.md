# Por qué no hay `.pkl`

Por tiempo, Modelado no exporta el modelo entrenado. En su lugar entrega las
predicciones ya calculadas en `data/predictions/`:

| Archivo | Contenido |
|---|---|
| `comparacion_modelos_rendimiento.csv` | Las 197 parcelas con el rendimiento observado y la predicción de cada modelo (del Modelo base al Modelo 5). En ENTRENAMIENTO son predicciones de validación cruzada. Es la entrada de `python main.py rendimientos`. |
| `rendimientos_estimados.csv` | Referencia del valor mostrado con el Modelo 5 (Ensamble Final tras selección de variables SBE, 16 variables). Una prueba verifica que la carga lo reproduce con 2 decimales. |

## Consecuencias

- La app **no hace inferencia**: lee `rendimientos_estimados`, que ya trae estado, municipio, superficie, coordenadas y rendimiento. `v_parcelas_app` sigue disponible si necesita además variables del maestro.
- Para cambiar de modelo basta con `python main.py rendimientos --modelo svr_19vars` (o `ETL_MODELO_VIGENTE` en `.env`). El esquema y la app no cambian.

## Modelos disponibles (2026-10-19)

Métricas sobre las 138 parcelas de ENTRENAMIENTO (validación cruzada):

| Modelo | `--modelo` | Columna del archivo | RMSE | MAE | R² |
|---|---|---|---|---|---|
| Modelo base: Random Forest Original (62 variables predictoras, KFold simple) | `rf_62vars` | M1_RF_Original_62vars | 0.575 | 0.433 | 0.541 |
| Modelo 1: Random Forest con Permutation Importance Out-of-Fold (OOF) (19 variables predictoras) | `rf_19vars` | M2_RF_Subconjunto_Optimo_19vars | 0.546 | 0.416 | 0.586 |
| Modelo 2: Random Forest con GridSearchCV (19 variables predictoras) | `rf_gridsearch_19vars` | M3_RF_Optimizado_GridSearch_19vars | 0.536 | 0.401 | 0.601 |
| Modelo de prueba: SVR con StandardScaler y kernel RBF (19 variables predictoras) | `svr_19vars` | M4_SVR_RBF_19vars | 0.510 | 0.390 | 0.638 |
| Modelo 3: Ensamble con Blending: 0.27 Random Forest + 0.73 SVR (19 variables predictoras) | `ensamble_19vars` | M5_Ensamble_19vars_27RF_73SVR | 0.506 | 0.386 | 0.644 |
| Modelo 4: Ensamble con Blending + Selección de Variables con Sequential Backward Elimination (16 variables predictoras) | sin clave | sin columna | 0.486 | no reportado | 0.671 |
| Modelo 5: Ensamble Final tras selección de variables SBE (16 variables predictoras) (vigente) | `ensamble_16vars` | M6_Ensamble_Final_SBE_16vars | 0.486 | 0.374 | 0.672 |

- Las predicciones se reproducen con los notebooks de `notebooks/` (`random_state=42`).
- Si más adelante existe un `.pkl`, va en `models/` (ignorado por git) y se sustituye este paso por la inferencia.
