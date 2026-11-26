-- ==============================================================================
-- 01-init-refugee-dbs.sql — Standalone PostgreSQL Initialization
-- Project: refugee-management
-- Target Database: refugee_management_db & refugee_bgtask_db
-- ==============================================================================

DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'refugee_user') THEN
      CREATE ROLE refugee_user WITH LOGIN PASSWORD 'refugee_dev_pass' CREATEDB;
   END IF;
END
$do$;

-- Ensure databases exist and are owned by refugee_user
SELECT 'CREATE DATABASE refugee_management_db OWNER refugee_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'refugee_management_db')\gexec

SELECT 'CREATE DATABASE refugee_bgtask_db OWNER refugee_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'refugee_bgtask_db')\gexec

GRANT ALL PRIVILEGES ON DATABASE refugee_management_db TO refugee_user;
GRANT ALL PRIVILEGES ON DATABASE refugee_bgtask_db TO refugee_user;
