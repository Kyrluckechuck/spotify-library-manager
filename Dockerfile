FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Update all image packages & install user-friendly cli editor
RUN apt-get update && apt-get upgrade -y && apt install nano mediainfo -y

# Install deps
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Pre-cache ffmpeg
RUN spotdl --download-ffmpeg

# Cleanup any APT leftovers
RUN apt clean && rm -rf /var/cache/apt/archives /var/cache/apt/lists

COPY ./spotify_library_sync/ /code/
