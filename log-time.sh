#!/bin/bash

archivo_log="$1"

# Verificar que se haya proporcionado el archivo de registro como argumento
if [ -z "$archivo_log" ]; then
  echo "Uso: $0 <ruta/del/archivo.log>"
  exit 1
fi

# Obtener la marca de tiempo de inicio
tiempo_inicio=$(cat "$archivo_log" | grep "Extracting from GitHub" | awk '{print $1, $2}' | head -n 1)

# Obtener la marca de tiempo de fin
tiempo_fin=$(cat "$archivo_log" | grep "Project ENQUEUE to CURADO published" | awk '{print $1, $2}' | tail -n 1)

# Convertir las marcas de tiempo a formato "epoch" (segundos desde 1970-01-01 00:00:00 UTC)
epoch_inicio=$(date -d "$tiempo_inicio" +%s)
epoch_fin=$(date -d "$tiempo_fin" +%s)

# Calcular la diferencia en segundos
tiempo_total=$((epoch_fin - epoch_inicio))

# Mostrar el tiempo total en formato legible
printf "Tiempo total: %02dh %02dm %02ds\n" $((tiempo_total / 3600)) $(((tiempo_total / 60) % 60)) $((tiempo_total % 60))

