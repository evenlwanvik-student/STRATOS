#!/bin/bash
# Shell script for stopping and removing existing images

sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)