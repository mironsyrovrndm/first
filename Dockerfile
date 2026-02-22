FROM python:3.12.11-bookworm

ENV DEBIAN_FRONTEND=nointeractive
ENV TERM=linux

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update -y --allow-unauthenticated --allow-insecure-repositories && \
    apt install -y wait-for-it curl htop

RUN pip install "poetry==1.8.3"

RUN mkdir -p /app
COPY poetry.lock pyproject.toml README.md /app/
WORKDIR /app
COPY src /app/src
COPY etc /app/etc

RUN poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false
