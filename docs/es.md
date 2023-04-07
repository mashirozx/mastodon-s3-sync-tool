# Herramienta de sincronización Mastodon S3 [es]

Una herramienta para la sincronización de objetos Mastodon S3.

*Este documento es una traducción de la versión en inglés realizada por ChatGPT.*

## Uso

### Conocimiento

Mastodon tiene cuatro tipos de carpetas en los objetos S3: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. Para cada tipo, hay una tabla en la base de datos que almacena el nombre del archivo, el tipo de contenido del archivo y la URL remota del archivo (si es un medio remoto en caché).

En este programa, leemos todos los registros de la base de datos que deben contener todos los archivos disponibles en estos cuatro tipos, y los descargamos del almacenamiento origen de S3, luego los subimos al almacenamiento destino de S3.

Tenemos cuatro trabajos para estos cuatro tipos, y puedes ejecutarlos por separado. Cada trabajo obtiene todos los registros de su tipo de la base de datos y agrega cada registro como tarea a la cola.

### Configuración

Puedes utilizar las variables de entorno para definir la ruta del archivo de configuración, o utilizar la ruta predeterminada `private/config.ini`. La plantilla del archivo de configuración es `private/config.sample.ini`. Y hay algo que debemos explicar:

#### `pg.tunnel`

En la mayoría de los casos, no debemos exponer la base de datos a la red pública, así que usamos un túnel ssh para conectarnos a la base de datos remota. pero puede que no necesites esto si estás ejecutando este programa en el mismo servidor remoto. Si usas un túnel, solo necesitas completar `localhost` en `pg.database.host`, ya que alcanzamos la base de datos a través de una conexión ssh.

#### `celery.concurrency`

Usamos memoria para almacenar en caché los archivos temporales descargados, y la memoria se liberará después de que finalice una tarea. Con el límite predeterminado del tamaño de archivo adjunto de medios de Mastodon, se utilizarán hasta 150Mb de memoria para cada tarea (concurrencia), y en mi caso de uso personal, tarda un promedio de 53 Mb. Puedes aumentar el espacio de intercambio para ejecutarse con una concurrencia más alta y evitar OOM. También debes considerar el ancho de banda de la red y el uso del CPU. Algunos proveedores de almacenamiento S3 tienen límites de tasa, es posible que debas establecer una concurrencia menor para evitar ser bloqueado y luego fallar en las tareas.

### Docker

Requisitos:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# copie y edite el archivo de configuración, por defecto el archivo de configuración es
# private/config.docker.ini en docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# inicie la cola (puerto UI web predeterminado 5555)
make du
# añadir trabajos
make dj

# alternativamente, puedes ejecutar los trabajos por separado:
# (puedes ejecutarlos en segundo plano, mira los bloques comentados en docker-compose.yml)
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### Manualmente

Requisitos:

- python >= 3.9
- redis >= 6

```bash
# crear virtualenv
make virtualenv
# ** ejecuta el comando impreso anteriormente para activar el virtualenv
# instalar dependencias
make install
# copiar y editar archivo de configuración
cp private/config.sample.ini private/config.ini
# Usamos tres procesos para ejecutar los servicios a continuación, puede
# que necesites tres terminales:
# 1. inicie la cola
make celery
# 2. iniciar interfaz web (puerto predeterminado 5555)
make flower
# 3. añadir trabajos
make jobs

# 3. si deseas ejecutar los trabajos por separado:
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## Registro

No soy un profesor de la biblioteca de colas Celery, pero puedes obtener todos sus registros a través de la interfaz web de celery - flower, que proporciona una interfaz web y API REST para verificar los registros.

## Desarrollo

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
