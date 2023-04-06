# Mastodon S3 Sync Tool

A tool for syncing Mastodon S3 objects.

Warning: **🚧 WORK IN PROGRESS 🚧**

## Usage

### Docker

Requirements:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# add jobs
make dj
```

### Manually

Requirements:

- python >= 3.9
- redis >= 6

```bash
make install
cp private/config.sample.ini private/config.ini
# start the queue
make celery
# start web UI (default port 5555)
make flower
# add jobs
make jobs
```

[Template](https://github.com/rochacbruno/python-project-template)
