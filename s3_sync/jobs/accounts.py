from s3_sync.services.pg import pg_query
from s3_sync.celery import accounts_task
from s3_sync.tasks.accounts import query, accounts
from s3_sync.utils.config import is_dev_mode
import signal

account_records = pg_query(query)

total = len(account_records)

killed = False


def handler(signum, frame):
    global killed
    print("\nSignal handler called with signal", signum)
    killed = True
    exit(130)


signal.signal(signal.SIGINT, handler)

for index, account in enumerate(account_records):
    if killed:
        print('Loop interrupted by user')
        break
    if is_dev_mode:
        print(f"[accounts] start {account[0]} - {index+1}/{total}")
        result = accounts(account, index, total)
        if (result):
            print(str(result))
        print(
            f"[accounts] {'skipped' if killed else 'done'} {account[0]} - {index+1}/{total}"
        )
    else:
        result = accounts_task.delay(account, index, total)
        # result.get()
        print(f"[accounts] added {account[0]} - {index+1}/{total}")
