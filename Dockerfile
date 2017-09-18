FROM python:2.7.13
MAINTAINER Will Price <will.price94@gmail.com>

RUN mkdir /src
WORKDIR /src

RUN apt-get update
RUN apt-get install -y dbus
RUN apt-get install -y libdbus-1-dev
RUN apt-get install -y libdbus-glib-1-dev

ADD Makefile /src/
ADD Pipfile /src/
RUN make init

ADD omxplayer tests setup.py setup.cfg tox.ini /src/
RUN pipenv run make test
