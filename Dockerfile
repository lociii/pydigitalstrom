FROM ubuntu:bionic

# system settings
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

# install packages
RUN apt-get update
RUN apt install -y software-properties-common vim curl git-core gcc make \
    zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libssl-dev wget  llvm\
    libffi-dev build-essential libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev liblzma-dev
RUN apt-get clean

# create app dir and user
RUN mkdir /app && useradd -m app

# change directory
WORKDIR /app

# change user
USER app

# set home directory to environment
ENV HOME /home/app

# install and setup pyenv
RUN git clone https://github.com/pyenv/pyenv.git ${HOME}/.pyenv
ENV PYENV_ROOT ${HOME}/.pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

# link requirements to container
ADD requirements.txt /app/
ADD requirements_test.txt /app/

# install required python versions
RUN pyenv install 3.5.6
RUN pyenv install 3.6.8
RUN pyenv install 3.7.2
RUN pyenv install 3.8-dev

RUN pyenv global 3.5.6 3.6.8 3.7.2 3.8-dev
RUN pyenv rehash

RUN python3.5 -m pip install pip --upgrade
RUN python3.6 -m pip install pip --upgrade
RUN python3.7 -m pip install pip --upgrade
RUN python3.8 -m pip install pip --upgrade

RUN pip3.5 install -r /app/requirements_test.txt
RUN pip3.6 install -r /app/requirements_test.txt
RUN pip3.7 install -r /app/requirements_test.txt
RUN pip3.8 install -r /app/requirements_test.txt

RUN pip install tox

ADD . /app/
