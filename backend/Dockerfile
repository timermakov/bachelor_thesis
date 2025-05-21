# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /usr/src/backend

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y \
	gcc \
	libpq-dev \
	python3-dev \
	libffi-dev \
	libssl-dev \
	cargo \
	wget \
	build-essential \
	&& apt-get clean

# Install TA-Lib from source
RUN wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz && \
	tar -xzf ta-lib-0.6.4-src.tar.gz && \
	cd ta-lib-0.6.4/ && \
	./configure --prefix=/usr && \
	make && \
	make install && \
	cd .. && \
	rm -rf ta-lib-0.6.4 ta-lib-0.6.4-src.tar.gz

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/backend/requirements.txt
RUN pip install -r requirements.txt


# copy project
COPY . /usr/src/backend/