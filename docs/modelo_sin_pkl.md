# Por qué no hay `.pkl`

Por tiempo, Modelado no exporta el modelo entrenado. En su lugar entrega las
predicciones ya calculadas en `data/predictions/`:

| Archivo | Contenido |
|---|---|
| `comparacion_modelos_rendimiento.csv` | Las 197 parcelas con el rendimiento observado y la predicción de cada modelo (`rf_50vars`, `rf_12vars`, `svr_12vars`). Es la entrada de `python main.py rendimientos`. |
| `rendimientos_estimados.csv` | Referencia del valor mostrado con el SVR de 12 variables. Una prueba verifica que la carga lo reproduce. |

## Consecuencias

- La app **no hace inferencia**: lee `rendimientos_estimados`, que ya trae estado, municipio, superficie, coordenadas y rendimiento. `v_parcelas_app` sigue disponible si necesita además variables del maestro.
- Para cambiar de modelo basta con `python main.py rendimientos --modelo rf_12vars` (o `ETL_MODELO_VIGENTE` en `.env`). El esquema y la app no cambian.
- Las predicciones se reproducen con los notebooks de `notebooks/` (`random_state=42`).
- Si más adelante existe un `.pkl`, va en `models/` (ignorado por git) y se sustituye este paso por la inferencia.
