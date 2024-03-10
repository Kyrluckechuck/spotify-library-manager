FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
RUN apt-get update && apt-get install -y ffmpeg aria2

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY ./spotify_library_sync/ /code/
