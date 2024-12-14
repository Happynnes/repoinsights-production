# Consolidada
La base de datos Consolidada almacena la información del proceso de desarrollo de los repositorios extraidos. Esta base de datos es utilizada para la visualización de los datos en Metabase.


## Respaldo 
El respaldo de la base de datos consolidada puede ser realizado de dos formas:
1. Utilizando un respaldo de la base de datos consolidada.
2. Utilizando una base de datos vacía y ejecutando el proceso de extraer y consolidar los datos.

### Utilizando un respaldo de la base de datos consolidada
1. Descargar el respaldo de la base de datos consolidada. Disponible en el siguiente url: [#](#)
2. Ejecutar el docker compose llamado docker-compose.local.yml. Para ello ejecutar el siguiente comando:
```bash
docker-compose -f docker-compose.local.yml up
```
Este comando levantará contenedores para los siguentes servicios.
1. Base de datos consolidada
2. Base de datos temporal
3. Servicio de extracción
4. Servicio de metricas y traspaso
5. RabbitMQ
6. Redis
Si se desea levantar solo la base de datos consolidada y la base de datos temporal, se debe ejecutar el siguiente comando:
```bash
docker-compose -f docker-compose.local.yml up db-consolidada db-temporal
```
3. El servicio del docker compose que levanta la base de datos consolidada es el siguiente:
```yaml
  consolidada:
    image: postgres
    restart: always
    environment:
      POSTGRES_USER: '${CONSOLIDADA_USER}'
      POSTGRES_DB: 'ghtorrent'
      POSTGRES_PASSWORD: '${CONSOLIDADA_PASS}'
    ports:
      - '${CONSOLIDADA_PORT}:${CONSOLIDADA_PORT}'
    expose:
      - '${CONSOLIDADA_PORT}'
    command: -p ${CONSOLIDADA_PORT}
    volumes:
      - ./docker/postgres-consolidada:/var/lib/postgresql/data
      - ./${DB_SCHEMA}:/docker-entrypoint-initdb.d/01-schema.sql
      - ./${DB_DATA}:/docker-entrypoint-initdb.d/02-data.sql
      - ./constraints.sql:/docker-entrypoint-initdb.d/03-constraints.sql
```
**Se debe reemplazar las variables de entorno por los valores correspondientes.**
Las variables DB_SCHEMA y DB_DATA. Son los archivos sql que contienen el esquema y los datos de la base de datos consolidada. Estos archivos se encuentran en el respaldo de la base de datos consolidada.
- **DB_SCHEMA:** Archivo sql que contiene el esquema de la base de datos.
- **DB_DATA:** Archivo sql que contiene los datos de la base de datos.

Esta es la base de datos que utiliza [Metabase](metabase.md) y [repoinsights-web](https://github.com/matiasbarram/repoinsights-web) para visualizar los datos