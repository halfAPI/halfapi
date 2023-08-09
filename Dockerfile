# syntax=docker/dockerfile:1
FROM python:3.11.4-alpine3.18
COPY . /halfapi
WORKDIR /halfapi
RUN apk update > /dev/null && apk add git > /dev/null
RUN pip install gunicorn uvicorn
RUN pip install .
CMD gunicorn halfapi.app

