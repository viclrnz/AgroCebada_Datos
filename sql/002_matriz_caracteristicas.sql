CREATE TABLE IF NOT EXISTS public.matriz_caracteristicas (
    id_poligono                  text NOT NULL,
    municipio                    text NOT NULL,
    estado                       text NOT NULL,
    conjunto                     text NOT NULL,
    area_ha_geod                 double precision NOT NULL,
    rendimiento_t_ha             double precision,
    diag_y_redondo               boolean,
    diag_y_resolucion            double precision,
    elev_media_m                 double precision NOT NULL,
    elev_std_m                   double precision NOT NULL,
    elev_min_m                   double precision NOT NULL,
    elev_max_m                   double precision NOT NULL,
    topo_cobertura_pix           double precision NOT NULL,
    pend_media_grados            double precision NOT NULL,
    pend_p90_grados              double precision NOT NULL,
    pend_max_grados              double precision NOT NULL,
    pend_cobertura_pix           double precision NOT NULL,
    ratio_cobertura_area         double precision NOT NULL,
    ratio_cobertura_pend         double precision NOT NULL,
    diag_topo_pocos_pix          boolean NOT NULL,
    diag_topo_nodata             boolean NOT NULL,
    z_pixel_clima_m              double precision NOT NULL,
    clima_pixel_id               text NOT NULL,
    dz_pixel_m                   double precision NOT NULL,
    pl_n_picos                   integer NOT NULL,
    pl_sos20_doy                 integer NOT NULL,
    pl_sos50_doy                 integer NOT NULL,
    pl_centro_pico_doy           integer NOT NULL,
    pl_eos50_doy                 integer NOT NULL,
    pl_eos20_doy                 integer NOT NULL,
    pl_duracion_dias             integer NOT NULL,
    pl_dias_meseta               integer NOT NULL,
    pl_caida_intra_ciclo         double precision NOT NULL,
    pl_ndvi_pico                 double precision NOT NULL,
    pl_ndvi_base                 double precision NOT NULL,
    pl_amplitud                  double precision NOT NULL,
    pl_integral_ciclo            double precision NOT NULL,
    pl_tasa_subida               double precision NOT NULL,
    pl_tasa_bajada               double precision NOT NULL,
    pl_hueco_max_critico         integer NOT NULL,
    diag_sin_ciclo               boolean NOT NULL,
    diag_ciclo_ambiguo           boolean NOT NULL,
    pl_ndvi_max_abr_oct          double precision NOT NULL,
    pl_ndvi_int_abr_oct          double precision NOT NULL,
    pl_ndvi_media_abr_oct        double precision NOT NULL,
    pl_lai_max_ciclo             double precision NOT NULL,
    pl_lai_int_ciclo             double precision NOT NULL,
    s2_n_picos                   integer NOT NULL,
    s2_sos50_doy                 integer NOT NULL,
    s2_centro_pico_doy           integer NOT NULL,
    s2_eos50_doy                 integer NOT NULL,
    s2_ndvi_pico                 double precision NOT NULL,
    s2_integral_ciclo            double precision NOT NULL,
    s2_ndvi_int_abr_oct          double precision NOT NULL,
    diag_s2_sin_ciclo            boolean NOT NULL,
    diag_fenologia_discrepante   boolean NOT NULL,
    ac_lluvia_pre_mm             double precision NOT NULL,
    ac_lluvia_veg_mm             double precision NOT NULL,
    ac_lluvia_flor_mm            double precision NOT NULL,
    ac_lluvia_llen_mm            double precision NOT NULL,
    ac_lluvia_ciclo_mm           double precision NOT NULL,
    ac_dias_lluvia_ciclo         integer NOT NULL,
    ac_lluvia_max_dia_ciclo_mm   double precision NOT NULL,
    ac_racha_seca_max_flor       integer NOT NULL,
    ac_racha_seca_max_ciclo      integer NOT NULL,
    ac_gdd_ciclo                 double precision NOT NULL,
    ac_gdd_hasta_flor            double precision NOT NULL,
    ac_eto_ciclo_mm              double precision NOT NULL,
    ac_balance_ciclo_mm          double precision NOT NULL,
    ac_balance_flor_mm           double precision NOT NULL,
    ac_balance_llen_mm           double precision NOT NULL,
    ac_lluvia_ciclo_anom_mm      double precision NOT NULL,
    ac_lluvia_ciclo_anom_rel     double precision NOT NULL,
    soil_arcilla_pct             double precision NOT NULL,
    soil_arena_pct               double precision NOT NULL,
    soil_soc_g_kg                double precision NOT NULL,
    soil_densidad_g_cm3          double precision NOT NULL,
    soil_ph                      double precision NOT NULL,
    soil_limo_pct                double precision NOT NULL,
    soil_agua_disp_mm            double precision NOT NULL,
    era5_dias_tmax28_flor        integer NOT NULL,
    era5_dias_tmax28_llen        integer NOT NULL,
    era5_dias_tmax30_flor        integer NOT NULL,
    era5_dias_tmax30_llen        integer NOT NULL,
    era5_tmax_media_flor_c       double precision NOT NULL,
    era5_vpd_medio_flor_kpa      double precision NOT NULL,
    era5_vpd_medio_llen_kpa      double precision NOT NULL,
    era5_sm1_siembra             double precision NOT NULL,
    era5_sm2_flor                double precision NOT NULL,
    era5_sm2_llen                double precision NOT NULL,
    era5_sm2_min_llen            double precision NOT NULL,
    era5_rs_ciclo_mj_m2          double precision NOT NULL,
    era5_apar_ciclo_mj_m2        double precision NOT NULL,
    era5_apar_post_pico_mj_m2    double precision NOT NULL,
    diag_era5_vecino             boolean NOT NULL,
    etl_run_id                   uuid NOT NULL,
    etl_cargado_en               timestamptz NOT NULL,
    etl_fuente_sha256            char(64) NOT NULL,
    CONSTRAINT matriz_caracteristicas_pk PRIMARY KEY (id_poligono),
    CONSTRAINT matriz_caracteristicas_id_formato CHECK (id_poligono ~ '^AGC_[0-9]{3}$'),
    CONSTRAINT matriz_caracteristicas_conjunto CHECK (conjunto IN ('ENTRENAMIENTO', 'PREDICCION')),
    CONSTRAINT matriz_caracteristicas_objetivo CHECK ((conjunto = 'ENTRENAMIENTO') = (rendimiento_t_ha IS NOT NULL))
);

COMMENT ON COLUMN public.matriz_caracteristicas.id_poligono IS 'identidad | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.municipio IS 'identidad | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.estado IS 'identidad | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.conjunto IS 'identidad | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.area_ha_geod IS 'features | Geometría de la parcela (WGS84) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.rendimiento_t_ha IS 'objetivo | Tabla de parcelas | ha';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_y_redondo IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_y_resolucion IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.elev_media_m IS 'features | INEGI CEM 120 m | m';
COMMENT ON COLUMN public.matriz_caracteristicas.elev_std_m IS 'features | INEGI CEM 120 m | m';
COMMENT ON COLUMN public.matriz_caracteristicas.elev_min_m IS 'podadas | INEGI CEM 120 m | m';
COMMENT ON COLUMN public.matriz_caracteristicas.elev_max_m IS 'podadas | INEGI CEM 120 m | m';
COMMENT ON COLUMN public.matriz_caracteristicas.topo_cobertura_pix IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pend_media_grados IS 'features | INEGI CEM 120 m | grados';
COMMENT ON COLUMN public.matriz_caracteristicas.pend_p90_grados IS 'features | INEGI CEM 120 m | grados';
COMMENT ON COLUMN public.matriz_caracteristicas.pend_max_grados IS 'features | INEGI CEM 120 m | grados';
COMMENT ON COLUMN public.matriz_caracteristicas.pend_cobertura_pix IS 'diagnostico | INEGI CEM 120 m | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ratio_cobertura_area IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ratio_cobertura_pend IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_topo_pocos_pix IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_topo_nodata IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.z_pixel_clima_m IS 'diagnostico | Tabla de parcelas | m';
COMMENT ON COLUMN public.matriz_caracteristicas.clima_pixel_id IS 'identidad | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.dz_pixel_m IS 'features | INEGI CEM 120 m vs. malla de clima 0.05° | m';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_n_picos IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_sos20_doy IS 'features | Planet, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_sos50_doy IS 'features | Planet, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_centro_pico_doy IS 'features | Planet, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_eos50_doy IS 'features | Planet, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_eos20_doy IS 'features | Planet, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_duracion_dias IS 'podadas | Planet, curva Whittaker λ=1000 | días';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_dias_meseta IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_caida_intra_ciclo IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_ndvi_pico IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_ndvi_base IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_amplitud IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_integral_ciclo IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_tasa_subida IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_tasa_bajada IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_hueco_max_critico IS 'diagnostico | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_sin_ciclo IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_ciclo_ambiguo IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_ndvi_max_abr_oct IS 'podadas | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_ndvi_int_abr_oct IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_ndvi_media_abr_oct IS 'podadas | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_lai_max_ciclo IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.pl_lai_int_ciclo IS 'features | Planet, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_n_picos IS 'features | Sentinel-2, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_sos50_doy IS 'features | Sentinel-2, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_centro_pico_doy IS 'features | Sentinel-2, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_eos50_doy IS 'podadas | Sentinel-2, curva Whittaker λ=1000 | día del año';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_ndvi_pico IS 'features | Sentinel-2, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_integral_ciclo IS 'features | Sentinel-2, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.s2_ndvi_int_abr_oct IS 'features | Sentinel-2, curva Whittaker λ=1000 | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_s2_sin_ciclo IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_fenologia_discrepante IS 'diagnostico | Tabla de parcelas | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_pre_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_veg_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_flor_mm IS 'podadas | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_llen_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_ciclo_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_dias_lluvia_ciclo IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_max_dia_ciclo_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_racha_seca_max_flor IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_racha_seca_max_ciclo IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_gdd_ciclo IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_gdd_hasta_flor IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_eto_ciclo_mm IS 'podadas | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_balance_ciclo_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_balance_flor_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_balance_llen_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_ciclo_anom_mm IS 'features | CHIRPS diario + CHIRTS corregido por elevación | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.ac_lluvia_ciclo_anom_rel IS 'features | CHIRPS diario + CHIRTS corregido por elevación | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_arcilla_pct IS 'features | SoilGrids 2.0 (0–30 cm) | %';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_arena_pct IS 'features | SoilGrids 2.0 (0–30 cm) | %';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_soc_g_kg IS 'features | SoilGrids 2.0 (0–30 cm) | g/kg';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_densidad_g_cm3 IS 'features | SoilGrids 2.0 (0–30 cm) | g/cm³';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_ph IS 'features | SoilGrids 2.0 (0–30 cm) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_limo_pct IS 'features | SoilGrids 2.0 (0–30 cm) | %';
COMMENT ON COLUMN public.matriz_caracteristicas.soil_agua_disp_mm IS 'features | SoilGrids 2.0 (0–30 cm) | mm';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_dias_tmax28_flor IS 'podadas | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_dias_tmax28_llen IS 'podadas | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_dias_tmax30_flor IS 'podadas | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_dias_tmax30_llen IS 'podadas | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_tmax_media_flor_c IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | °C';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_vpd_medio_flor_kpa IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | kPa';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_vpd_medio_llen_kpa IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | kPa';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_sm1_siembra IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_sm2_flor IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_sm2_llen IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_sm2_min_llen IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | adimensional / índice';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_rs_ciclo_mj_m2 IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | MJ/m²';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_apar_ciclo_mj_m2 IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | MJ/m²';
COMMENT ON COLUMN public.matriz_caracteristicas.era5_apar_post_pico_mj_m2 IS 'features | ERA5-Land diario (Tmax con delta CHIRTS) | MJ/m²';
COMMENT ON COLUMN public.matriz_caracteristicas.diag_era5_vecino IS 'diagnostico | Tabla de parcelas | adimensional / índice';

