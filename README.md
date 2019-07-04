# Stratos

Visualizing netCDF files from SINMOD, OSCAR and DREAM on a web page.

This is a temporary structure for displaying a single netcdf file in web page.

To start the server in a container: sudo bash start.sh
Check for existing images in the container: sudo docker ps -a
To stop and remove existing images: sudo bash stop.sh
t
Authors: Even Wanvik and Maria Skårdal


# How to run the server inside the container:

in powershell:
    Set-NetConnectionProfile -interfacealias "vEthernet (DockerNAT)" -NetworkCategory Private

open docker desktop settings (right corner), enable shared C-drive

Run these in terminal:
    docker build -t stratos .
    docker run stratos


# Commands to run server in container with mounted volume (aka access to the local NetCDF files)
Terminal:
    docker build -t stratos .
    docker run -it -p 5000:5000 -v %cd%:/app -v C:\Users\marias\Documents\NetCDF_data:/data stratos /bin/bash

Once inside the container run:
    set FLASK_APP=app.py
    flask run -h 0.0.0.0

# How to push image to container registry
1. Login to azure registry:
    az acr login --name stratoscontainers
2. Build the image:
    docker build -t stratos .
3. Tag the image:
    docker tag <Image_ID> stratoscontainers.azurecr.io/name
4. Push it to the registry
    docker push stratoscontainers.azurecr.io/name


