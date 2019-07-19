# Docker container for web microservice and netCDF API

# Use latest stable ubuntu OS as Docker image upon which to run the container\

FROM continuumio/miniconda3
#FROM python:3.6

MAINTAINER Maria Skårdal & Even Wanvik

# Update and/or install necesarry dependencies and libraries
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org
RUN conda install -c conda-forge zarr

EXPOSE 80

ENV STATIC_URL /static
ENV FLASK_APP app.py


CMD ["python", "-m", "flask", "run", "-p", "80", "-h", "0.0.0.0"]


