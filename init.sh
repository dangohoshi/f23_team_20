#!/bin/bash

sudo rm -f db.sqlite3

sudo rm -rf lifesync/migrations/*
sudo touch lifesync/migrations/__init__.py

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
