# Mastodon S3同步工具 [zh]

一个用于同步Mastodon S3对象的工具。

*本文档由 ChatGPT 翻译自英文文档*

## 用途

### 知识

Mastodon在S3存储中有四种类型的文件夹：`media_attachments`，`accounts`，`custom_emojis`，`preview_cards`。对于每一种类型，数据库中都有一个表来存储文件名、文件内容类型以及文件远程URL（如果文件被从远程缓存）。

在这个程序中，首先我们从数据库读取所有记录，这些记录应该包含这四种类型的所有可用文件。然后从源S3存储下载它们，最后上传到目标S3存储。

我们为每种类型的文件提供了四个作业，您可以单独运行它们。每个作业从数据库中获取其类型的所有记录，并将每个记录添加到队列中作为任务。

### 配置

您可以使用环境变量定义配置文件路径，或者使用默认路径`private/config.ini`。配置文件模板是`private/config.sample.ini`。有一些需要解释的内容：

#### `pg.tunnel`

在大多数情况下，我们不应该将数据库暴露在公共网络中，所以我们使用ssh隧道连接到远程数据库。但是，如果您在同一远程服务器上运行此程序，则可能不需要此选项。如果使用隧道，则只需在`pg.database.host`中填写127.0.0.1（或任何其他私有网络地址），因为我们是通过ssh隧道到达数据库的。

#### `celery.concurrency`

我们使用内存缓存已下载的临时文件，任务完成后内存将被释放。根据Mastodon的默认媒体附件大小限制，每个任务（并发）最多使用150Mb内存，在我的个人用例中，平均需要53 Mb。您可以增加swap空间以使用更高的并发性并避免OOM。此外，您还应考虑网络带宽和CPU使用率。某些S3存储提供者有速率限制，您可能需要设置较低的并发性以避免被阻止。

### Docker

要求：

- docker>=20.10.16
- docker-compose >= 2.6.0

```bash
#复制并编辑配置文件，默认配置文件位于
#private/config.docker.ini in docker-compose.yml
cp private/config.sample.ini private/config.docker.ini

#启动队列（默认web UI端口5555）
make du
#添加作业
make dj

#您也可以单独运行作业：
#（您可以在后台运行它们，请参见docker-compose.yml中的注释块）
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### 手动

要求：

- python>=3.9
- redis>=6

```bash
#创建虚拟环境
make virtualenv
# **运行上面打印的命令来激活虚拟环境**
#安装依赖项
make install
#复制并编辑配置文件
cp private/config.sample.ini private/config.ini
#我们使用三个进程运行下面的服务，您可能需要三个终端：
# 1. 启动队列
make celery
# 2. 启动web UI（默认端口5555）
make flower
# 3.添加作业
make jobs

# 3.如果您想分别运行作业：
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## 日志

我不是Celery队列库的专家。您可以通过Celery的Web UI-Flower获取其所有日志，Flower提供了Web界面和REST API以检查日志。

## 常见问题解答

### 怎样在同步被中断后继续同步？如何限制同步范围？

你可以使用 `--limit` 选项来限制同步记录的数量。例如，如果你想同步1000条记录，可以运行以下命令：

```bash
python -m s3_sync.jobs.media_attachments --limit 1000
```

如果你想在同步中断后继续同步，可以使用 `--offset` 选项来跳过前N条记录。例如，如果你想跳过前1000条记录并继续同步，可以运行以下命令：

```bash
python -m s3_sync.jobs.media_attachments --offset 1000
```

同时使用 `--limit` 和 `--offset` 选项也是可以的。

## 开发

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
