FROM python:3.7.6-stretch

# create app dir and user
RUN mkdir /app
RUN useradd -m app

# change directory
WORKDIR /app

# change user
USER app

# set home directory to environment
ENV HOME /home/app

# link requirements to container
ADD requirements.txt /app/
ADD requirements_test.txt /app/

ENV PATH /home/app/.local/bin:${PATH}

RUN pip install --user -r /app/requirements_test.txt

ADD . /app/
