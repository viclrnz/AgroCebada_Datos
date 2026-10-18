-- Tabla principal del Front: una fila por parcela con todo lo que muestra la app.
-- ENTRENAMIENTO lleva el rendimiento observado y PREDICCION el del modelo vigente.
-- `modelo` permite cambiar de SVR a RF sin tocar el esquema ni la app.
-- Coordenadas en WGS84 (EPSG:4326): centroide de la parcela, o un punto
-- interior si el centroide cae fuera del polígono.
CREATE TABLE IF NOT EXISTS public.rendimientos_estimados (
    id_poligono                  text NOT NULL,
    estado                       text NOT NULL,
    municipio                    text NOT NULL,
    conjunto                     text NOT NULL,
    superficie_ha                double precision NOT NULL,
    latitud                      double precision NOT NULL,
    longitud                     double precision NOT NULL,
    rendimiento_estimado_t_ha    numeric(5, 2) NOT NULL,
    origen                       text NOT NULL,
    modelo                       text,
    etl_run_id                   uuid NOT NULL,
    etl_cargado_en               timestamptz NOT NULL,
    etl_fuente_sha256            char(64) NOT NULL,
    CONSTRAINT rendimientos_estimados_pk PRIMARY KEY (id_poligono),
    CONSTRAINT rendimientos_estimados_parcela FOREIGN KEY (id_poligono)
        REFERENCES public.matriz_caracteristicas (id_poligono),
    CONSTRAINT rendimientos_estimados_origen CHECK (origen IN ('observado', 'modelo')),
    CONSTRAINT rendimientos_estimados_modelo CHECK ((origen = 'modelo') = (modelo IS NOT NULL)),
    CONSTRAINT rendimientos_estimados_rango CHECK (rendimiento_estimado_t_ha BETWEEN 0.1 AND 15)
);

-- Si la tabla se creó con la primera versión (sin ubicación), agrega las columnas.
-- Quedan nulas hasta la siguiente ejecución de `python main.py rendimientos`.
ALTER TABLE public.rendimientos_estimados
    ADD COLUMN IF NOT EXISTS estado        text,
    ADD COLUMN IF NOT EXISTS municipio     text,
    ADD COLUMN IF NOT EXISTS conjunto      text,
    ADD COLUMN IF NOT EXISTS superficie_ha double precision,
    ADD COLUMN IF NOT EXISTS latitud       double precision,
    ADD COLUMN IF NOT EXISTS longitud      double precision;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'rendimientos_estimados_coordenadas') THEN
        ALTER TABLE public.rendimientos_estimados ADD CONSTRAINT rendimientos_estimados_coordenadas
            CHECK (latitud BETWEEN 18 AND 21.5 AND longitud BETWEEN -99.5 AND -97);
    END IF;
END
$$;

COMMENT ON COLUMN public.rendimientos_estimados.superficie_ha IS 'area_ha_geod del maestro | ha';
COMMENT ON COLUMN public.rendimientos_estimados.latitud IS 'WGS84 | centroide o punto interior de la parcela';
COMMENT ON COLUMN public.rendimientos_estimados.longitud IS 'WGS84 | centroide o punto interior de la parcela';
COMMENT ON COLUMN public.rendimientos_estimados.rendimiento_estimado_t_ha IS 'Rendimiento a mostrar | t/ha, 2 decimales';
COMMENT ON COLUMN public.rendimientos_estimados.origen IS 'observado (ENTRENAMIENTO) o modelo (PREDICCION)';
COMMENT ON COLUMN public.rendimientos_estimados.modelo IS 'Modelo que generó el valor, p. ej. svr_12vars; nulo si es observado';
