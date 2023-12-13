# syntax=docker/dockerfile:1
FROM python:alpine3.19
COPY . /halfapi
WORKDIR /halfapi
ENV VENV_DIR=/opt/venv
RUN mkdir -p $VENV_DIR
RUN python -m venv $VENV_DIR
RUN $VENV_DIR/bin/pip install gunicorn uvicorn
RUN $VENV_DIR/bin/pip install .
RUN ln -s $VENV_DIR/bin/halfapi /usr/local/bin/
CMD $VENV_DIR/bin/gunicorn halfapi.app
