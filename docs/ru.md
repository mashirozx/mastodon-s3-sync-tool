# Инструмент синхронизации Mastodon S3 [ru]

Инструмент для синхронизации объектов Mastodon S3.

*Этот документ переведен с английской версии ChatGPT.*

## Использование

### Знания

Mastodon имеет четыре типа папок в объектах S3: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. Для каждого типа есть таблица в базе данных, которая хранит имя файла, тип содержимого файла и удаленный URL-адрес файла (если это кэшированный удаленный файл).

В этой программе мы читаем все записи из базы данных, которые должны содержать все доступные файлы этих четырех типов, и загружаем их из исходного хранилища S3, а затем загружаем их в целевое хранилище S3.

У нас есть четыре задания для этих четырех типов, и вы можете запускать их отдельно. Каждая работа получает все записи своего типа из базы данных и добавляет каждую запись как задание в очередь.

### Конфигурация

Вы можете использовать переменные окружения, чтобы определить путь к файлу конфигурации или использовать путь по умолчанию — `private/config.ini`. Образец файла конфигурации находится в `private/config.sample.ini`. И что-то нужно объяснить:

#### `pg.tunnel`

В большинстве случаев мы не должны раскрывать базу данных в общедоступной сети, поэтому мы используем ssh-туннель для подключения к удаленной базе данных. Но вам может не понадобиться это, если вы запускаете эту программу на том же удаленном сервере. Если используется туннель, достаточно заполнить localhost в `pg.database.host`, поскольку мы связываемся с базой данных через ssh-соединение.

#### `celery.concurrency`

Мы используем память для кэширования временных файлов, загруженных из S3, и память будет освобождаться после завершения каждой задачи. С учетом ограничения размера вложений медиафайлов по умолчанию в Mastodon, на каждую задачу (конкурентность) будет использовано до 150 Мб памяти, а в моем личном случае в среднем требуется 53 Мб. Вы можете увеличить раздел подкачки, чтобы работать с более высокой конкурентностью и избежать ошибок OOM. Также стоит учитывать пропускную способность сети и использование процессора. Некоторые провайдеры хранилищ S3 имеют ограничение на скорость, вам может потребоваться установить более низкую конкурентность, чтобы избежать блокировки и сбоев задач.

### Docker

Требования:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# скопируйте и отредактируйте файл конфигурации; по умолчанию файл конфигурации находится в 
# private/config.docker.ini в docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# add jobs
make dj

# или вы можете запускать задания отдельно:
# (можно запустить в фоновом режиме, см. закомментированные блоки в docker-compose.yml)
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### Ручной

Требования:

- python >= 3.9
- redis >= 6

```bash
# create virtualenv
make virtualenv
# ** run the command printed above to activate the virtualenv
# install dependencies
make install
# copy and edit config file
cp private/config.sample.ini private/config.ini
# We use three processes to run the services below, you may 
# need three terminals:
# 1. start the queue
make celery
# 2. start web UI (default port 5555)
make flower
# 3. add jobs
make jobs

# 3. if you want to run the jobs separately:
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## Журналирование

Я не профессор библиотеки очередей Celery, но вы можете получить все ее журналы через интерфейс веб-UI - flower, который предоставляет веб-интерфейс и REST-API для проверки журналов.

## Development

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
