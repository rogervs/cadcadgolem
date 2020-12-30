FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt -qq -y install git curl python3 python3-venv python3-pip
RUN python3 -m venv /opt/venv
RUN bash -c 'source /opt/venv/bin/activate && pip3 install -U pip && pip3 install wheel cadcad dill'
WORKDIR /golem/work
VOLUME /golem/work /golem/output /golem/resource
