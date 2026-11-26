FROM python:3.12.11-alpine3.22

ARG FASTAPI_COMMON_REF=1.1.7

RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers make \
 && apk add --no-cache bash git gettext libpq-dev libffi-dev openssl-dev

WORKDIR /app

RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir \
        "greenlet" \
        "jinja2" \
        "psycopg[binary]" \
        "openg2p-fastapi-common==1.1.6" \
        "openg2p-fastapi-auth==1.1.6" \
        "openg2p-fastapi-auth-models==1.1.6"

COPY vendor/pbms/openg2p-pbms-models /src/openg2p-pbms-models
COPY vendor/pbms/openg2p-bg-task-models /src/openg2p-bg-task-models
COPY vendor/pbms/openg2p-bg-task-celery-beat-producers /src/openg2p-bg-task-celery-beat-producers

RUN pip install --no-cache-dir \
        /src/openg2p-pbms-models \
        /src/openg2p-bg-task-models \
        /src/openg2p-bg-task-celery-beat-producers

RUN apk del --no-network .build-deps

ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "openg2p_bg_task_celery_beat_producers.main.celery_app", "worker", "--beat", "--loglevel=info", "--schedule=/tmp/celery-beat-schedule.db"]
