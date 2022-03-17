# syntax=docker/dockerfile:1
FROM docker.io/python:3.8.12-slim-bullseye
COPY . /halfapi
WORKDIR /halfapi
RUN apt-get update > /dev/null && apt-get -y install git > /dev/null
RUN pip install gunicorn uvicorn
# Install package with extra_requires for testing
RUN pip install ".[tests]"
ENV PYTHONPATH=./tests
RUN pytest
CMD gunicorn halfapi.app

