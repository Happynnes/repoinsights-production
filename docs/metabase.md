# Metabase

Se utiliza Metabase para la visualización de los datos de la base de datos.
Metabase utiliza una sola base de datos para almacenar sus datos, por lo que se debe crear una base de datos en el servidor de base de datos para Metabase.
El respaldo de la base de datos de Metabase se realiza de forma manual.

## Restaurar base de datos
1. Descargar el respaldo de la base de datos de Metabase. Disponible en el siguiente url: [https://drive.google.com/file/d/1EUprujRC4jYQOtMymaRZNZCH26PApkWv/view?usp=sharing](Google Drive)
2. Crear un contenedor de Docker utilizando la imagen de Postgres. Para ello se puede utilizar docker compose. Un ejemplo es 
```yaml
  metabase-db:
    image: postgres
    restart: always
    environment:
      POSTGRES_USER: '${MB_POSTGRES_USER}'
      POSTGRES_DB: '${MB_POSTGRES_DB}'
      POSTGRES_PASSWORD: '${MB_POSTGRES_PASSWORD}'
    ports:
      - '${MB_DB_PORT}:${MB_DB_PORT}'
    expose:
      - '${MB_DB_PORT}'
    command: -p '${MB_DB_PORT}'
    volumes:
      - ./docker/postgres-metabase:/var/lib/postgresql/data

```
Se debe reemplazar las variables de entorno por los valores correspondientes.
**Importante: El usuario y la contraseña deben ser los mismos que se utilizaron para crear la base de datos de Metabase. El puerto puede ser el mismo o diferente. Para solicitar la información contactarse con matias.barra64@gmail.com**

3. Utilizar el comando pg_restore para restaurar la base de datos. El comando es el siguiente:
```bash
pg_restore -c -U <usuario> -p <puerto> -h <host> -d <nombre_base_datos> -v "<ruta_archivo_respaldo>" -W
```
Para más información sobre el comando pg_restore visitar el siguiente enlace: [https://www.postgresql.org/docs/9.1/app-pgrestore.html](https://www.postgresql.org/docs/9.1/app-pgrestore.html)

4. Levantar el contenedor de Metabase. Para ello se puede utilizar docker compose. Un ejemplo es 
```yaml
  metabase:
    image: metabase/metabase:latest
    restart: always
    ports:
      - 8080:3000
    environment:
      MB_DB_FILE: ~/repoinsights/docker/metabase-data/metabase.db
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: '${MB_POSTGRES_DB}'
      MB_DB_PORT: '${MB_DB_PORT}'
      MB_DB_USER: '${MB_POSTGRES_USER}'
      MB_DB_PASS: '${MB_POSTGRES_PASSWORD}'
      MB_DB_HOST: '${MB_DB_HOST}'
      MB_SEND_EMAIL_ON_FIRST_LOGIN_FROM_NEW_DEVICE: FALSE
    depends_on:
      - metabase-db
```

5. Ingresar a la aplicación de Metabase. La url es la siguiente: [http://localhost:8080](http://localhost:8080)
6. Ingresar con el usuario y contraseña correspondiente. Para solicitar la información contactarse con matias.barra64@gmail.com
7. En la sección de administración, en la pestaña de base de datos, se debe cambiar el nombre de la base de datos por el nombre de la base de datos consolidada. Para configurar la base de datos consolidada revisar [consolidada.md](consolidada.md)