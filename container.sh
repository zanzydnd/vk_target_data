#!/bin/sh
git pull
docker-compose stop
docker-compose rm -f
docker-compose up --build