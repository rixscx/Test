FROM python:3.7.3-slim-stretch

ENV DEBIAN_FRONTEND noninteractive

# Update sources.list to point to the Debian archive AND disable security checks for it
RUN echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list

# Install build tools and ALL required C libraries
RUN apt-get -qq update && \
    apt-get -qq install -y --allow-unauthenticated build-essential gcc g++ make git libjpeg-dev zlib1g-dev libffi-dev liblmdb-dev unzip wget && \
    apt-get --purge autoremove --yes && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
# Increased timeout for pip
RUN pip install --default-timeout=600 -r requirements.txt --no-cache-dir

RUN mkdir /src
COPY . /src
WORKDIR /src