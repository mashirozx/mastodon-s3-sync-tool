# Mastodon S3 Sync Tool

A tool for syncing Mastodon S3 objects.

## 🚧 Project Status 🚧

Ready for use, but still under test.

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
# create virtualenv
make virtualenv
# ** run the command printed above to activate the virtualenv
# install dependencies
make install
cp private/config.sample.ini private/config.ini
# we use three processes to run the services below, you may need three terminals:
# 1. start the queue
make celery
# 2. start web UI (default port 5555)
make flower
# 3. add jobs
make jobs

# 3. if you want to run the jobs manually:
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## Development

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```

[Template](https://github.com/rochacbruno/python-project-template)
