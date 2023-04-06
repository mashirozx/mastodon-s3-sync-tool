from s3_sync.services.pg import pg_query
from s3_sync.celery import accounts_task
from s3_sync.tasks.accounts import query, accounts

account_records = pg_query(query)

total = len(account_records)

print(f"total accounts: {total}")


for index, account in enumerate(account_records):
    if (account[0] == -99):
        continue
    else:
        result = accounts_task.delay(account, index, total)
        # accounts(account, index, total)
        # print(str(account))
        # result.get()
        print(f"[accounts] added {account[0]} - {index+1}/{total}")
