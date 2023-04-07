# Mastodon S3 Sync Tool [en]

A tool for syncing Mastodon S3 objects.

## Usage

### Knowledge

Mastodon has four types of the folder in S3 storages: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. For each type, there is a table in the database to store the file name, file content type, and file remote URL (if the file is cached from remote).

In this program, we first read all the records from the database, which should contain all the available files in these four types. And then download them from the source S3 storage, and later upload them into the destination S3 storage.

We have four jobs for each of these types of files, and you can run them separately. Each job gets all the records of its type from the database and adds each record as a task into the queue.

### Configurations

You can use the environment variables to define the config file path, or use the default path `private/config.ini`. The config file template is `private/config.sample.ini`. And there is something that need to be explained:

#### `pg.tunnel`

In most cases, we shouldn't expose the database to the public network, so we use an ssh tunnel to connect to the remote database. But you may not need this if you are running this program on the same remote server. If using a tunnel, you just need to fill in 127.0.0.1 (or any other private network address) in `pg.database.host`, since we are reaching the database through an ssh tunnel.

#### `celery.concurrency`

We use memory to cache the downloaded temporary files, and the memory will be released later after the task is finished. With Mastodon's default media attachment size limit, up to 150Mb memory will be used for each task (concurrency), and in my personal use case, it takes 53 Mb on average. You can increase the swap space to run with a higher concurrency and avoid OOM. Also, you should consider the network bandwidth and CPU usage. Some S3 storage provider has a rate limit, you may need to set a lower concurrency to avoid being blocked.

### Docker

Requirements:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# copy and edit the config file, the default config file is
# private/config.docker.ini in docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# add jobs
make dj

# Alternatively, you can run the jobs separately:
# (you can run them in the background, see commented blocks in docker-compose.yml)
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
# copy and edit the config file
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

I'm not an expert on the queue library Celery. You can get all its logs through Celery's Web UI - flower, which provides a web interface and REST API to check the logs.

## FAQ

### How to continue the sync after it's interrupted? How to limit the sync range?

You can use the `--limit` option to limit the number of records to be synced. For example, if you want to sync 1000 records, you can run the command below:

```bash
python -m s3_sync.jobs.media_attachments --limit 1000
```

If you want to continue the sync after it's interrupted, you can use the `--offset` option to skip the first N records. For example, if you want to skip the first 1000 records and continue the sync, you can run the command below:

```bash
python -m s3_sync.jobs.media_attachments --offset 1000
```

It's OK to use both `--limit` and `--offset` options at the same time.

## Development

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
