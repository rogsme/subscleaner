FROM python:alpine

RUN apk update && apk add --no-cache curl gcc g++ make libxml2-dev libxslt-dev tzdata && \
    pip install --no-cache-dir subscleaner

RUN echo -e "SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n\n" > /etc/crontabs/root

CMD echo "$CRON find /files -name \"*.srt\" | $(which subscleaner)" >> /etc/crontabs/root && crond -f
