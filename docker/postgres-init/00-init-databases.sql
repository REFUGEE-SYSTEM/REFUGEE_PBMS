SELECT 'CREATE DATABASE bgtaskdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bgtaskdb')\gexec
