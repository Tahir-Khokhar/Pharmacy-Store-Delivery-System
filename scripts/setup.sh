#!/usr/bin/env bash
set -e

echo "=== Setting up PharmaCare Pharmacy Platform ==="
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_pharmacy_data
python manage.py collectstatic --noinput
echo "=== PharmaCare Setup Complete! ==="
