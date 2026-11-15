#!/usr/bin/env bash
# Render build script: installs packages, prepares the database and static files.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations accounts gym appearance --noinput
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Creates plans, trainers, classes, website content and the 'admin' user
# (password from the DJANGO_ADMIN_PASSWORD environment variable). Safe to run on every deploy.
python manage.py seed_demo
