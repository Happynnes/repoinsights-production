# Extraction
Los servicios que se encargan de la extracción de datos son los siguientes:
1. Repositorios pendientes
2. Extracción
3. Métricas y traspaso

## Dependencias
Para ejecutar los servicios de extracción, se requiere tener instalado Docker y Docker Compose. Además, se requiere tener un archivo `.env` con las variables de entorno necesarias para la ejecución de los servicios. El archivo `.env`.

## Docker compose
El archivo `docker-compose.local.yml` contiene la configuración de los servicios de extracción. Para ejecutar los servicios.

## Repositorios pendientes
Este servicio se encarga de obtener los repositorios que aún no han sido procesados por el servicio de extracción. Para esto, se conecta a la base de datos de consolidada y obtiene los repositorios que no han sido procesados. Luego, los envía a la cola de RabbitMQ para que el servicio de extracción los procese.
Este servicio se encuentra en el archivo `services/pendientes_service/`.
Dentro del docker compose se encuentra definido como `pendientes_service`.

```yaml
  pendientes_service:
    build:
      context: .
      dockerfile: Dockerfile.pendientes
    restart: always
    env_file:
      - .env
    depends_on:
      - rabbitmq
      - consolidada
    environment:
      - RABBIT_HOST=rabbitmq
      - CONSOLIDADA_IP=consolidada
      - PYTHONUNBUFFERED=1
```

## Extracción
Este servicio se encarga de extraer la información del proceso de desarrollo de los repositorios de GitHub. Utiliza la API de GitHub para obtener la información de los repositorios. Extrae la información de los repositorios y la almacena en la base de datos temporal. Luego, envía la información a la cola de RabbitMQ para que el servicio de métricas y traspaso la procese.
Este servicio se encuentra en el archivo `services/extract_service/`.
```yaml
  extract_service:
    build:
      context: .
      dockerfile: Dockerfile.extract
    restart: always
    env_file:
      - .env
    depends_on:
      - rabbitmq
      - temporal
      - redis
    environment:
      - RABBIT_HOST=rabbitmq
      - TEMP_IP=temporal
      - REDIS_HOST=redis
      - PYTHONUNBUFFERED=1
    deploy:
      replicas: 2
    volumes:
      - ./docker/extract_service:/app/logs
```

## Métricas y traspaso
Una vez almacenada la información en temporal, este servicio se encarga de procesarla y almacenarla en la base de datos consolidada. Para esto, se conecta a la base de datos temporal y obtiene la información de los repositorios. Una vez traspasada la información, genera las métricas y las almacena en la base de datos consolidada. 
Este servicio se encuentra en el archivo `services/metrics_service/`.
```yaml
  traspaso_service:
    build:
      context: .
      dockerfile: Dockerfile.traspaso
    restart: always
    env_file:
      - .env
    depends_on:
      - rabbitmq
      - temporal
      - consolidada
    environment:
      - RABBIT_HOST=rabbitmq
      - TEMP_IP=temporal
      - CONSOLIDADA_IP=consolidada
      - PYTHONUNBUFFERED=1
    volumes:
      - ./docker/trapaso_service:/app/logs
```