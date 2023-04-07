# Outil de synchronisation Mastodon S3 [fr]

Un outil pour synchroniser les objets Mastodon S3.

*Ce document est traduit à partir de la version anglaise par ChatGPT.*

## Utilisation

### Connaissances

Mastodon a quatre types de dossiers dans les objets S3: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. Pour chaque type, il y a une table dans la base de données pour stocker le nom du fichier, le type de contenu du fichier et l'URL distante du fichier (s'il s'agit de fichiers médias mis en cache à distance).

Dans ce programme, nous lisons tous les enregistrements de la base de données qui devraient contenir tous les fichiers disponibles dans ces quatre types, et les téléchargeons depuis le stockage S3 source, puis les envoyons au stockage S3 de destination.

Nous avons quatre emplois pour ces quatre types, et vous pouvez les exécuter séparément. Chaque travail récupère tous les enregistrements de son type depuis la base de données, et ajoute chaque enregistrement en tant que tâche à la file d'attente.

### Configuration

Vous pouvez utiliser les variables d'environnement pour définir le chemin du fichier de configuration, ou utiliser le chemin par défaut `private/config.ini`. Le modèle de fichier de configuration est `private/config.sample.ini`. Et il y a quelque chose qui doit être expliqué:

#### `pg.tunnel`

Dans la plupart des cas, nous ne devrions pas exposer la base de données au réseau public, donc nous utilisons un tunnel ssh pour se connecter à la base de données distante. mais cela peut ne pas être nécessaire si vous exécutez ce programme sur le même serveur distant. Si vous utilisez un tunnel, il suffit de remplir localhost dans `pg.database.host`, car nous accédons à la base de données via une connexion ssh.

#### `celery.concurrency`

Nous utilisons la mémoire pour mettre en cache les fichiers temporaires téléchargés, et la mémoire sera libérée après qu'une tâche est terminée. Avec la limite de taille d'attachement multimédia par défaut de Mastodon, jusqu'à 150 Mo de mémoire seront utilisés pour chaque tâche (concurrence), et dans mon cas d'utilisation personnel, cela prend en moyenne 53 Mo. Vous pouvez augmenter l'espace d'échange pour exécuter avec une concurrence plus élevée et éviter les erreurs de type OOM. Vous devriez également tenir compte de la bande passante réseau et de l'utilisation du processeur. Certains fournisseurs de stockage S3 ont des limites de débit, vous devrez peut-être définir une concurrence inférieure pour éviter d'être bloqué et que les tâches échouent.

### Docker

Exigences:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# copier et modifier le fichier de configuration, par défaut le fichier de configuration est
# private/config.docker.ini in docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# ajouter des tâches
make dj

# alternatively, you are able to run the jobs separately:
# (you can run them in background, see commented blocks in docker-compose.yml)
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### Manuellement

Exigences:

- python >= 3.9
- redis >= 6

```bash
# créer le virtualenv
make virtualenv
# ** exécutez la commande imprimée ci-dessus pour activer le virtualenv
# installer les dépendances
make install
# copier et modifier le fichier de configuration
cp private/config.sample.ini private/config.ini
# Nous utilisons trois processus pour exécuter les services ci-dessous, vous pouvez
# besoin de trois terminaux:
# 1. start the queue
make celery
# 2. star web UI (default port 5555)
make flower
# 3. add jobs
make jobs

# 3. si vous voulez exécuter les tâches séparément:
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## Logging

Je ne suis pas un professeur de la bibliothèque de files d'attente Celery, mais vous pouvez obtenir tous ses journaux via l'interface Web de Celery - flower, qui fournit une interface Web et une API REST pour vérifier les journaux.

## Développement

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
