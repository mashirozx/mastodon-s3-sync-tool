# マストドン S3 同期ツール [ja]

Mastodon S3オブジェクトを同期するためのツールです。

*このドキュメントはChatGPTによって英語版から翻訳されました。*

## 使用法

### 知識

Mastodonには、S3オブジェクト内に4種類のフォルダがあります:`media_attachments` 、 `accounts` 、 `custom_emojis` 、`preview_cards` 。 それぞれのタイプに対して、ファイル名、ファイルコンテンツタイプ、および（キャッシュされたリモートメディアの場合）ファイルリモートURLを保存するためのデータベース内のテーブルがあります。

このプログラムでは、これら4つのタイプのすべての利用可能なファイルが含まれているはずのデータベースからすべてのレコードを読み取り、ソースS3ストレージからダウンロードし、それらを宛先S3ストレージにアップロードします。

これら4つのタイプには4つのジョブがあり、それぞれを個別に実行できます。各ジョブは、データベースからそのタイプのすべてのレコードを取得し、それぞれのレコードをキューのタスクとして追加します。

### Config

環境変数を使用して構成ファイルのパスを定義するか、デフォルトパスである `private/config.ini` を使用できます。 構成ファイルテンプレートは`private/config.sample.ini`です。 説明する必要があるものがあります：

#### `pg.tunnel`

ほとんどの場合、データベースをパブリックネットワークに公開すべきではないため、リモートデータベースに接続するにはsshトンネルを使用します。 ただし、このプログラムを同じリモートサーバーで実行している場合は、これは必要ありません。 トンネルを使用する場合は、`pg.database.host`にlocalhostを記入するだけでよく、ssh接続を介してデータベースに到達するためです。

#### `celery.concurrency`

ダウンロードした一時的なファイルをキャッシュするためにメモリを使用し、メモリは1つのタスクが終了すると解放されます。 Mastodonのデフォルトのメディア添付ファイルサイズ制限により、1つのタスク（並行性）ごとに最大150Mbのメモリが使用され、私の個人的な使用例では平均で53 Mbかかります。 スワップスペースを増やして、より高い並列処理で実行し、OOMを回避しましょう。 また、ネットワーク帯域幅とCPU使用率も考慮する必要があります。 一部のS3ストレージプロバイダにはレート制限があるため、ブロックされてタスクが失敗しないように、より低い並行性を設定する必要がある場合があります。

### Docker

要件：

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# configファイルをコピーして編集します。デフォルトのconfigファイルは、
# docker-compose.yml内のprivate/config.docker.iniです。
cp private/config.sample.ini private/config.docker.ini
# キューを開始します（デフォルトのWeb UIポート5555）
make du
# ジョブを追加します
make dj

# 代わりに、ジョブを個別に実行できます：
# （バックグラウンドで実行できます。docker-compose.ymlのコメントされたブロックを参照してください）
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### 手動

要件：

- python >= 3.9
- redis >= 6

```bash
# virtualenvを作成します。
make virtualenv
# ** 仮想環境を有効にするには、上記で表示されたコマンドを実行してください。
# 依存関係をインストールします
make install
# configファイルをコピーして編集します
cp private/config.sample.ini private/config.ini
# 以下のサービスを実行するために3つのプロセスを使用します。あなたは必要かもしれません
# 三つのターミナル：
# 1. キューを開始する
make celery
# 2. Web UIを開始する（デフォルトポート5555）
make flower
# 3. ジョブを追加します
make jobs

# 3.ジョブを個別に実行したい場合：
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## ロギング

私はキューライブラリCeleryの教授ではありませんが、CeleryのWeb UI-flowerを介してすべてのログを取得できます。フラワーは、ログを確認するためのWebインターフェイスとREST APIを提供します。

## 開発

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
