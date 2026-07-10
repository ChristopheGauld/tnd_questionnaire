#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements-django.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata myhcl_tnd_seed
