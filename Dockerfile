FROM ubuntu:xenial

ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get -y update && apt-get -y install \
      build-essential \
      gcc \
      python3.6 \
      python3.6-dev \
      python3-pip \
      python3.6-venv \
      libssl-dev \
    && \
    apt-get clean && \
    mkdir /app && \
    useradd -m app

WORKDIR /app

USER app

ADD requirements.txt /app/
ADD requirements_test.txt /app/

ENV PATH /home/app/venv/bin:${PATH}

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN python3.6 -m venv ~/venv && \
    pip install -r /app/requirements_test.txt

ADD . /app/
