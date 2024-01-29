FROM python:3.8.18-alpine3.18


RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app
RUN apk --update add python3 py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del build-dependencies


ADD spyBot.py /app
ADD speedrun.py /app
ADD db.py /app
ADD sheets.py /app