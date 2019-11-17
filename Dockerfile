FROM python:3.7-stretch

# system settings
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

# install packages
RUN apt-get update
RUN apt install -y git-core gcc make python3-dev python-virtualenv
RUN apt-get clean

# create app dir and user
RUN mkdir /app
RUN useradd -m app

# change directory
WORKDIR /app

# change user
USER app

# update path
ENV PATH /home/app/venv/bin:$PATH

# link requirements to container
ADD requirements.txt /app/
ADD requirements_test.txt /app/

RUN virtualenv --python=/usr/local/bin/python --system-site-packages /home/app/venv
RUN pip install --force-reinstall setuptools
RUN pip install pip --upgrade
RUN pip install -r /app/requirements_test.txt

ADD . /app/
