-- Mantiene una interfaz estable para la app Django.
-- Django usa esta vista con un modelo `managed = False`, así los cambios de la
-- tabla no obligan a cambiar la app.
-- La vista expone solo las columnas que necesita la interfaz.
CREATE OR REPLACE VIEW public.v_parcelas_app AS
SELECT
    id_poligono,
    municipio,
    estado,
    conjunto,
    area_ha_geod,
    rendimiento_t_ha,
    elev_media_m,
    pend_media_grados,
    pl_ndvi_pico,
    pl_sos50_doy,
    pl_eos50_doy,
    ac_lluvia_ciclo_mm,
    soil_ph,
    etl_cargado_en
FROM public.matriz_caracteristicas;
