FROM --platform=linux/amd64 ubuntu:20.04 as dev
WORKDIR /thesis

# Install python3.9
RUN apt update && \
    apt -y install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt -y install python3.9 && \
    apt -y install libcairo2-dev

# Set default python3.9
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install ssh, git, pip, venv, sshpass, nano
RUN apt update && \
    apt-get -y install git openssh-client python3-pip python3.9-dev python3.9-venv sshpass openssh-server nano tmux &&\
    pip install -U black

# Install ping
RUN apt-get update && apt-get install -y iputils-ping && apt-get install -y nmap && apt-get install -y iproute2

# Create virtual environments
ADD ./requirements.txt /thesis/backend/
RUN pip install --upgrade pip
RUN pip install -r /thesis/backend/requirements.txt

WORKDIR /thesis/backend

FROM python:3.9.16-alpine3.16 as main

WORKDIR /thesis

#Install python 3
RUN apk add --update --no-cache py3-pip

RUN apk add py3-virtualenv 
RUN apk add python3-dev build-base py3-numpy linux-headers py3-dbus 
RUN apk add cairo py3-cairo cairo-dev gobject-introspection py3-gobject3 gobject-introspection-dev
RUN apk add dbus-glib-dev

#Install requirement for snappy C
RUN apk add snappy-dev

#Install other platform requirement
RUN apk add libffi-dev

# Install utility
RUN apk update && \
    apk add git openssh-client sshpass openssh-server nano tmux pkgconfig &&\
    pip install -U setuptools wheel

RUN apk update && apk add iputils nmap iproute2

FROM main as test

# Install utility
RUN apk update && \
    pip install -U black

ADD ./requirements.txt /thesis/backend/

# Download and install pip package
RUN pip install --upgrade pip
RUN pip install -r /thesis/backend/requirements.txt

#Copy file
ADD ./ /thesis/backend/

WORKDIR /thesis/backend

FROM main as prod
ADD ./requirements.txt /thesis/backend/

# Download and install pip package
RUN pip install --upgrade pip
RUN pip install -r /thesis/backend/requirements.txt

#Copy file
ADD ./ /thesis/backend/

WORKDIR /thesis/backend
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]