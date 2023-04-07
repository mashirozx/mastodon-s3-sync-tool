# Mastodon S3 Sync Tool [en]

A tool for syncing Mastodon S3 objects.

## Usage

### Knowledge

Mastodon has four types of folder in S3 objects: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. For each type, there is a table in database to store the file name, file content type, and file remote url (if is cached remote media).

In this program, we read all records form database that should contain all the available files in these four types, and download theme from the source S3 storage, the upload them to the destination S3 storage.

We have four jobs for these four types, and you can run them separately. Each job get all the records of it's type from database, and add each record as task to the queue.

### Config

You can use the environment variables to define the config file path, or use the default path `private/config.ini`. The config file template is `private/config.sample.ini`. And there is something need to be explained:

#### `pg.tunnel`

In most cases, we shouldn't expose the database to the public network, so we use a ssh tunnel to connect to the remote database. but you may not need this if you are running this program on the same remote server. If using a tunnel, just need to fill in localhost in `pg.database.host`, since we reach the database through a ssh connection.

#### `celery.concurrency`

We use memory to cache the downloaded temporary files, and the memory will be release after one task is finished. With Mastodon's default media attachment size limit, up to 150Mb memory will be used for each task (concurrency), and in my personal use case, it takes 53 Mb on average. You can increase the swap space to run with a higher concurrency and avoid OOM. Also you should consider the network bandwidth and the CPU usage. Some S3 storage provider has rate limit, you may need to set a lower concurrency to avoid being blocked and then the tasks fail.

### Docker

Requirements:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# copy and edit config file, by default config file is
# private/config.docker.ini in docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# add jobs
make dj

# alternatively, you are able to run the jobs separately:
# (you can run them in background, see commented blocks in docker-compose.yml)
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### Manually

Requirements:

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

## Logging

I'm not a professor of queue library Celery, but you are able to get all its log through Celery's Web UI - flower, which provides a web interface and rest API to check the logs.

## Development

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
