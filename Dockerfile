# syntax=docker/dockerfile:1
FROM docker.io/python:3.8.12-slim-bullseye
COPY . /halfapi
WORKDIR /halfapi
RUN pip install .
CMD gunicorn halfapi.app

