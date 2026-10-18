-- Mantiene una interfaz estable para la app Django.
-- Django usa esta vista con un modelo `managed = False`, así los cambios de la
-- tabla no obligan a cambiar la app.
-- Las columnas nuevas van al final: CREATE OR REPLACE VIEW no permite
-- reordenar ni quitar columnas existentes.
CREATE OR REPLACE VIEW public.v_parcelas_app AS
SELECT
    m.id_poligono,
    m.municipio,
    m.estado,
    m.conjunto,
    m.area_ha_geod,
    m.rendimiento_t_ha,
    m.elev_media_m,
    m.pend_media_grados,
    m.pl_ndvi_pico,
    m.pl_sos50_doy,
    m.pl_eos50_doy,
    m.ac_lluvia_ciclo_mm,
    m.soil_ph,
    m.etl_cargado_en,
    r.rendimiento_estimado_t_ha,
    r.origen                     AS origen_rendimiento,
    r.modelo                     AS modelo_rendimiento,
    r.latitud,
    r.longitud
FROM public.matriz_caracteristicas AS m
LEFT JOIN public.rendimientos_estimados AS r USING (id_poligono);
