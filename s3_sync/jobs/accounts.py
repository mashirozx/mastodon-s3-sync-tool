from s3_sync.services.pg import pg_query
from s3_sync.celery import accounts_task
from s3_sync.tasks.accounts import query, accounts
from s3_sync.utils.job_config import *
import signal

account_records = pg_query(query(limit))

total = len(account_records)

killed = False


def handler(signum, frame):
    global killed
    print("\nSignal handler called with signal", signum)
    killed = True
    exit(130)


signal.signal(signal.SIGINT, handler)

for index, account in enumerate(account_records):
    (
        id,
        avatar_file_name, avatar_content_type, avatar_remote_url,
        header_file_name, header_content_type, header_remote_url
    ) = account

    if killed:
        print('Loop interrupted by user')
        break
    if avatar_file_name == None and header_file_name == None:
        print(f"[accounts] skipped {id} - {index+1}/{total}")
        continue
    if is_dev_mode:
        print(f"[accounts] start {id} - {index+1}/{total}")
        result = accounts(account, index, total)
        if (result):
            print(str(result))
        print(
            f"[accounts] {'skipped' if killed else 'done'} {id} - {index+1}/{total}"
        )
    else:
        result = accounts_task.delay(account, index, total)
        # result.get()
        print(f"[accounts] added {id} - {index+1}/{total}")
