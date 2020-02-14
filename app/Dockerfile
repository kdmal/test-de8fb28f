FROM python:3.8.1-alpine

ENV VERSION 1.0

COPY ./requirements.txt /tmp/requirements.txt
RUN set -ex \
    && apk --no-cache update \
    && apk --no-cache upgrade \
    && apk --no-cache add \
        sqlite \
    && apk add --no-cache --virtual .build-deps \
        make \
        gcc \
        musl-dev \
    && pip3 --no-cache-dir install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && apk del --no-cache .build-deps \
    && pip freeze

RUN set -ex \
    && mkdir -p /app/flaskr \
    && touch /app/.keep
WORKDIR /app
