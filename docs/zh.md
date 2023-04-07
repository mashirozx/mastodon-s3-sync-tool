# Mastodon S3同步工具 [zh]

这是一个用于同步 Mastodon S3 objects 的工具。

*本文档由 ChatGPT 翻译自英文文档*

## 用法

### 知识

Mastodon 在 S3 objects 中有四种文件夹类型：`media_attachments`、`accounts`、`custom_emojis`、`preview_cards`。对于每种类型，在数据库中都有一张表来存储文件名、文件内容类型和文件远程 URL（如果是缓存的远程媒体）。

在这个程序中，我们从数据库中读取所有记录，这些记录应该包含了这四种类型中所有可用的文件，并从源 S3 存储器下载它们，然后将它们上传到目标 S3 存储器中。

我们为这四种类型准备了四个任务，并可以单独运行它们。每个任务从数据库获取它所属类型的所有记录，并将每个记录作为任务添加到队列中。

### 配置

您可以使用环境变量定义配置文件路径，或者使用默认路径 `private/config.ini`。配置文件模板为 `private/config.sample.ini`。还有一些需要解释的内容：

#### `pg.tunnel`

在大多数情况下，我们不应该将数据库暴露在公共网络中，因此我们使用 ssh 隧道连接到远程数据库。但是，如果您在同一台远程服务器上运行此程序，则可能不需要此项。如果使用隧道，只需在 `pg.database.host` 中填写 localhost，因为我们通过 ssh 连接到数据库。

#### `celery.concurrency`

我们使用内存来缓存下载的临时文件，当一个任务完成后，这些内存就会被释放。根据 Mastodon 的默认媒体附件大小限制，每个任务（并发）最多使用 150Mb 内存，在我的个人用例中，平均占用 53 Mb。您可以增加交换空间以提高并发性能，并避免 OOM。还应考虑网络带宽和 CPU 使用率。一些 S3 存储提供商有速率限制，您可能需要设置较低的并发性来避免被阻止，然后任务失败。

### Docker

要求：

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# 拷贝并编辑配置文件，默认配置文件在docker-compose.yml中的private/config.docker.ini
cp private/config.sample.ini private/config.docker.ini
# 启动队列（默认Web UI端口5555）
make du
# 添加任务
make dj

# 或者，您可以单独运行任务：
# （您可以在后台运行它们，请参见docker-compose.yml中的注释块）
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### 手动

要求：

- python >= 3.9
- redis >= 6

```bash
# 创建virtualenv
make virtualenv
# ** 运行上面打印出来的命令以激活虚拟环境
# 安装依赖项
make install
# 拷贝并编辑配置文件
cp private/config.sample.ini private/config.ini
# 我们使用三个进程来运行以下服务，您可能需要三个终端：
# 1. 启动队列
make celery
# 2. 启动Web UI（默认端口5555）
make flower
# 3. 添加任务
make jobs

# 3. 如果您想单独运行任务：
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## 日志

我不是Celery队列库的教授，但您可以通过Celery的Web UI-flower获取所有日志，它提供了一个Web界面和rest API来检查日志。

## 开发

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
