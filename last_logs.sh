#!/bin/bash

# El primer argumento al script es N.
N=$1

# Encuentra todos los archivos .log, extrae las fechas, convierte a segundos desde la Época Unix y ordena.
for file in $(find . -name '*.log'); do
    # Extrae la fecha del nombre del archivo.
    date_str=$(echo $file | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}')

    # Convierte la fecha a segundos desde la Época Unix.
    date_sec=$(date -d "$date_str" +%s)

    # Imprime la fecha en segundos y el nombre del archivo.
    echo $date_sec $file
done | sort -rn | awk -v n=$N '{
    # Convierte los segundos a una fecha legible.
    system("date -d @"$1" -u +\"%Y-%m-%dT%H:%M:%SZ\"")

    # Imprime el nombre del archivo.
    print $2

    # Si hemos impreso n líneas, sale.
    if (NR >= n) exit
}'
