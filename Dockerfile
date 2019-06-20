# Docker container for web microservice and netCDF API

# Use latest stable ubuntu OS as Docker image upon which to run the container\
#FROM ubuntu:latest
FROM python:3.6

MAINTAINER Even Wanvik "evenlwanvik@gmail.com"

# Update and/or install necesarry dependencies and libraries
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV STATIC_URL /static
ENV STATIC_PATH /home/even/Workspaces/STRATOS/app/static

ENTRYPOINT ["python"]
CMD ["app.py"]