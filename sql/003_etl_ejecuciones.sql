-- Guarda el resultado de cada ejecución para auditoría y seguimiento.
CREATE TABLE IF NOT EXISTS public.etl_ejecuciones (
    run_id           uuid PRIMARY KEY,
    inicio           timestamptz NOT NULL,
    fin              timestamptz NOT NULL,
    estado           text NOT NULL CHECK (estado IN ('OK', 'ERROR_CONTRATO', 'ERROR')),
    filas_fuente     integer,
    filas_afectadas  integer,
    fuente_sha256    char(64),
    advertencias     integer,
    mensaje          text
);
