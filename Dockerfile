FROM python:3.11-slim-buster as builder
MAINTAINER Plesoun Ltd
ENV LANG C.UTF-8

RUN set -ex \
	&& apt-get -y update \
	&& apt-get -y upgrade

RUN pip3 install \
	pysolarmanv5 

RUN mkdir -p /app/gatherer

COPY . /app/gatherer

WORKDIR /app/gatherer
CMD ["python3", "/app/gatherer/solar_gatherer.py"]
