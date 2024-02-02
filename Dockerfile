FROM python:3.11-slim

ENV VIRTUAL_ENV=/app/env

RUN mkdir -p /app/bot && \
    apt update && apt upgrade -y --no-install-recommends locales libzbar0 && \
    echo 'de_DE.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && update-locale LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 && \
    python3 -m venv $VIRTUAL_ENV && \
    apt-get clean && rm -rf /var/lib/apt/* /var/cache/apt/*

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY bot/requirements.txt /app/bot/
WORKDIR /app

RUN apt update && apt install -y build-essential g++ gcc && \
    pip install --upgrade pip setuptools wheel && \
    pip install uwsgi pytz Flask pillow && \
    pip install -r bot/requirements.txt && \
    apt remove -y build-essential g++ && apt autoremove -y && \
    rm -rf /var/lib/apt/* /var/cache/apt/*

COPY bot/ /app/bot
COPY server/ /app/server

STOPSIGNAL SIGINT
CMD ["python", "/app/bot/trash.py"]
