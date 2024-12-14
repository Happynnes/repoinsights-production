#!/bin/bash

BACKUP_FILE="consolidada_db.tar"
export PGPASSWORD="$POSTGRES_PASSWORD"
export PGUSER="$POSTGRES_USER"
export PGPORT="$DB_PORT"
export PGDB="$POSTGRES_DB"

error_exit() {
    echo "$1" 1>&2
    exit 1
}

if [ ! -f "$BACKUP_FILE" ]; then
    error_exit "Error: El archivo de respaldo $BACKUP_FILE no existe."
fi
# Restaurar la base de datos desde el archivo .tar
pg_restore -c -U "$PGUSER" -p "$PGPORT" -d ghtorrent_restore_2015 -v $BACKUP_FILE -W
if [ $? -ne 0 ]; then
    error_exit "Error: La restauración de la base de datos falló."
fi

echo "La base de datos $PGDB ha sido restaurada exitosamente desde $BACKUP_FILE."
