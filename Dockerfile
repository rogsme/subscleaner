FROM python:alpine

RUN apk add --no-cache curl \
 && SUPERCRONIC_SHA1SUM=71b0d58cc53f6bd72cf2f293e09e294b79c666d8 \
 && SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 \
 && curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  supercronic-linux-amd64" | sha1sum -c - \
 && chmod +x supercronic-linux-amd64 \
 && mv supercronic-linux-amd64 /usr/local/bin/supercronic \
 && apk del curl

RUN mkdir -p /data

RUN pip install --no-cache-dir subscleaner

CMD echo "${CRON:-0 0 * * *} find /files -name \"*.srt\" | $(which subscleaner) --db-location /data/subscleaner.db" > /crontab && \
    /usr/local/bin/supercronic /crontab
