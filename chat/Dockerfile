FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y \
	supervisor python3-dev python3-pip

RUN mkdir -p /usr/src/
COPY . /usr/src
WORKDIR /usr/src

RUN pip3 install poetry && poetry install --only main
COPY ./supervisor.conf /etc/supervisor/conf.d/

RUN mkdir -p /usr/src/app/logs/
CMD ["supervisord", "-n"]
