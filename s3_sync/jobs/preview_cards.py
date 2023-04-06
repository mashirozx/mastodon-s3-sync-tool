from s3_sync.services.pg import pg_query
from s3_sync.celery import preview_cards_task
from s3_sync.tasks.preview_cards import query, preview_cards
from s3_sync.utils.job_config import *
import signal

preview_card_records = pg_query(query(limit))

total = len(preview_card_records)

killed = False


def handler(signum, frame):
    global killed
    print("\nSignal handler called with signal", signum)
    killed = True
    exit(130)


signal.signal(signal.SIGINT, handler)

for index, preview_card in enumerate(preview_card_records):
    if killed:
        print('Loop interrupted by user')
        break
    if is_dev_mode:
        print(f"[preview_cards] start {preview_card[0]} - {index+1}/{total}")
        result = preview_cards(preview_card, index, total)
        if (result):
            print(str(result))
        print(
            f"[preview_cards] {'skipped' if killed else 'done'} {preview_card[0]} - {index+1}/{total}"
        )
    else:
        result = preview_cards_task.delay(preview_card, index, total)
        # result.get()
        print(f"[preview_cards] added {preview_card[0]} - {index+1}/{total}")
