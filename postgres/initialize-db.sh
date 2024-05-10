#!/bin/bash
echo "Creating the database named ${POSTGRES_DB}"
set -e
DB_EXISTS=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='docker_call'")
if [ "$DB_EXISTS" != '1' ]; then
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE docker_call"
fi
