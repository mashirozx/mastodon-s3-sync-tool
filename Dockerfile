FROM python:3.9-alpine

RUN apk add --no-cache postgresql-libs postgresql-dev gcc musl-dev libffi-dev make

COPY requirements.txt /app/requirements.txt
COPY requirements-test.txt /app/requirements-test.txt
COPY setup.py /app/setup.py
COPY s3_sync/VERSION /app/s3_sync/VERSION
COPY README.md /app/README.md

WORKDIR /app

RUN pip install .
COPY . /app

CMD ["s3_sync"]
