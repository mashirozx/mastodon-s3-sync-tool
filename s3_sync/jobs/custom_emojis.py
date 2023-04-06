from s3_sync.services.pg import pg_query
from s3_sync.celery import custom_emojis_task
from s3_sync.tasks.custom_emojis import query, custom_emojis
from s3_sync.utils.config import is_dev_mode
import signal

custom_emoji_records = pg_query(query)

total = len(custom_emoji_records)

killed = False


def handler(signum, frame):
    global killed
    print("\nSignal handler called with signal", signum)
    killed = True
    exit(130)


signal.signal(signal.SIGINT, handler)

for index, custom_emoji in enumerate(custom_emoji_records):
    if killed:
        print('Loop interrupted by user')
        break
    if is_dev_mode:
        print(f"[custom_emojis] start {custom_emoji[0]} - {index+1}/{total}")
        result = custom_emojis(custom_emoji, index, total)
        if (result):
            print(str(result))
        print(
            f"[custom_emojis] {'skipped' if killed else 'done'} {custom_emoji[0]} - {index+1}/{total}"
        )
    else:
        result = custom_emojis_task.delay(custom_emoji, index, total)
        # result.get()
        print(f"[custom_emojis] added {custom_emoji[0]} - {index+1}/{total}")
