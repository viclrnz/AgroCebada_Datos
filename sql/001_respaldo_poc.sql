-- La PoC creó la tabla sin llave primaria porque usó df.to_sql con replace.
-- El upsert necesita una llave para resolver los conflictos.
-- Si la tabla existe sin PK, se conserva como respaldo y 002 crea la versión correcta.
DO $$
BEGIN
    IF to_regclass('public.matriz_caracteristicas') IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conrelid = to_regclass('public.matriz_caracteristicas') AND contype = 'p'
        ) THEN
            ALTER TABLE public.matriz_caracteristicas RENAME TO matriz_caracteristicas_poc_respaldo;
            RAISE NOTICE 'Tabla de la PoC renombrada a matriz_caracteristicas_poc_respaldo';
        END IF;
    END IF;
END
$$;