#!/bin/bash

docker-compose exec core python manage.py migrate
