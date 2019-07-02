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
RUN pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

#This command is necessary to build docker image from windows
#RUN chmod 644 app.py 

ENV STATIC_URL /static
ENV STATIC_PATH /home/even/Workspaces/STRATOS/app/static

CMD ["/bin/bash"]
#ENTRYPOINT ["app.py"]

# Run in powershell:
# Set-NetConnectionProfile -interfacealias "vEthernet (DockerNAT)" -NetworkCategory Private

# Run these in terminal:
# docker build -t stratos .
# docker run -it -p 5000:5000 -v %cd%:/app -v C:\Users\marias\Documents\NetCDF_data:/data stratos /bin/bash

# Once inside the container run:
# set FLASK_APP=app.py
# flask run -h 0.0.0.0
