#!/bin/bash
# Shell script for building an image from the Dockerfile

app="stratos"

docker build -t ${app} .

docker run -d -p 5000:5000 \
  --name=${app} \
  -v $PWD:/app ${app}