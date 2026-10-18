-- Usuario de base de datos para el chatbot, de solo lectura.
-- Solo puede consultar la tabla del Front, la vista de la app y la matriz de
-- características (el prompt del chatbot las usa). No ve la bitácora del ETL ni
-- las tablas de Django (auth_user guarda las contraseñas).
-- La contraseña no se versiona. Se asigna una sola vez en el SQL Editor de Supabase:
--   ALTER ROLE chatbot_lector WITH LOGIN PASSWORD '<contraseña segura>';
-- y se guarda en el .env del servicio del chatbot.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'chatbot_lector') THEN
        CREATE ROLE chatbot_lector NOLOGIN;
    END IF;
END
$$;

-- Evita que el rol herede permisos amplios del esquema público.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM chatbot_lector;
GRANT USAGE ON SCHEMA public TO chatbot_lector;
GRANT SELECT ON public.rendimientos_estimados, public.v_parcelas_app, public.matriz_caracteristicas TO chatbot_lector;

-- Límites para que una consulta del chatbot no sature la base.
ALTER ROLE chatbot_lector SET default_transaction_read_only = on;
ALTER ROLE chatbot_lector SET statement_timeout = '5s';
ALTER ROLE chatbot_lector CONNECTION LIMIT 5;
