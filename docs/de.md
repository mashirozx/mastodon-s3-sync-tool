# Mastodon S3 synchronisieren tool [de]

Ein Tool zum Synchronisieren von Mastodon S3-Objekten.

*Dieses Dokument wurde aus der englischen Version von ChatGPT übersetzt.*

## Verwendung

### Kenntnisse

Mastodon hat vier Arten von Ordnern in S3-Objekten: `media_attachments`, `accounts`, `custom_emojis`, `preview_cards`. Für jeden Typ gibt es eine Tabelle in der Datenbank, in der der Dateiname, der Dateiinhaltstyp und die URL (sofern Medien zwischengespeichert werden) gespeichert sind.

In diesem Programm lesen wir alle Datensätze aus der Datenbank, die alle verfügbaren Dateien dieser vier Typen enthalten sollten, und laden sie aus dem Quell-S3-Speicher herunter und laden sie dann auf den Ziel-S3-Speicher hoch.

Wir haben vier Jobs für diese vier Typen, und Sie können sie separat ausführen. Jeder Job ruft alle Datensätze seines Typs aus der Datenbank ab und fügt jeden Datensatz als Aufgabe zur Warteschlange hinzu.

### Konfiguration

Sie können Umgebungsvariablen verwenden, um den Pfad zur Konfigurationsdatei zu definieren oder den Standardpfad `private/config.ini` zu verwenden. Die Konfigurationsdateivorlage ist `private/config.sample.ini`. Und es gibt etwas zu erklären:

#### `pg.tunnel`

In den meisten Fällen sollten wir die Datenbank nicht im öffentlichen Netzwerk freigeben, daher verwenden wir einen SSH-Tunnel, um uns mit der remote Datenbank zu verbinden. Aber wenn Sie dieses Programm auf demselben Remote-Server ausführen, benötigen Sie dies möglicherweise nicht. Wenn Sie einen Tunnel verwenden, müssen Sie nur localhost in `pg.database.host` eingeben, da wir auf die Datenbank über eine SSH-Verbindung zugreifen.

#### `celery.concurrency`

Wir verwenden Speicher, um die heruntergeladenen temporären Dateien zu puffern, und der Speicher wird nach Abschluss einer Aufgabe freigegeben. Mit Mastodons Standard-Medienanhanggrößenbegrenzung werden für jede Aufgabe (Concurrency) bis zu 150 MB Speicher verwendet, und in meinem persönlichen Anwendungsfall beträgt dies durchschnittlich 53 MB. Sie können den Swap-Speicher erhöhen, um mit einer höheren Parallelität auszuführen und OOM-Fehler zu vermeiden. Sie sollten auch die Netzwerkbandbreite und die CPU-Auslastung berücksichtigen. Einige S3-Speicheranbieter haben Rate-Limits. Möglicherweise müssen Sie die Parallelität reduzieren, um zu vermeiden, dass die Aufgaben blockiert werden und fehlschlagen.

### Docker

Anforderungen:

- docker >= 20.10.16
- docker-compose >= 2.6.0

```bash
# Kopieren und Bearbeiten der Konfigurationsdatei, standardmäßig befindet sich die Konfigurationsdatei in
# private/config.docker.ini in docker-compose.yml
cp private/config.sample.ini private/config.docker.ini
# start the queue (default web UI port 5555)
make du
# jobs hinzufügen
make dj

# Alternativ können Sie die Jobs separat ausführen:
# (Sie können sie im Hintergrund ausführen. Weitere Informationen finden Sie in den auskommentierten Blöcken in docker-compose.yml)
docker compose exec celery sh -c 'python -m s3_sync.jobs.media_attachments'
docker compose exec celery sh -c 'python -m s3_sync.jobs.accounts'
docker compose exec celery sh -c 'python -m s3_sync.jobs.custom_emojis'
docker compose exec celery sh -c 'python -m s3_sync.jobs.preview_cards'
```

### Manuell

Anforderungen:

- python >= 3.9
- redis >= 6

```bash
# virtuelle Umgebung erstellen
make virtualenv
# ** führen Sie den oben gedruckten Befehl aus, um die virtualenv zu aktivieren.
# Abhängigkeiten installieren
make install
# Kopieren und Bearbeiten der Konfigurationsdatei
cp private/config.sample.ini private/config.ini
# Wir verwenden drei Prozesse, um die folgenden Dienste auszuführen. Sie benötigen möglicherweise drei Terminals:
# 1. Queue starten
make celery
# 2. Starten Sie das Web UI (Standardport 5555).
make flower
# 3. jobs hinzufügen
make jobs

#3. Wenn Sie die Jobs separat ausführen möchten:
python -m s3_sync.jobs.media_attachments
python -m s3_sync.jobs.accounts
python -m s3_sync.jobs.custom_emojis
python -m s3_sync.jobs.preview_cards
```

## Protokollierung

Ich bin kein Professor der Queue-Bibliothek Celery, aber Sie können alle seine Protokolle über Celerys Web-UI - flower erhalten, das eine Web-Schnittstelle und REST-API zum Überprüfen der Protokolle bereitstellt.

## Entwicklung

```bash
python -m s3_sync.jobs.media_attachments --dev --limit 10
python -m s3_sync.jobs.accounts --dev --limit 10
python -m s3_sync.jobs.custom_emojis --dev --limit 10
python -m s3_sync.jobs.preview_cards --dev --limit 10
```
