#!/usr/bin/env bash
set -e

echo "=== Seeding PharmaCare Demo & Clinical Data ==="
python manage.py seed_pharmacy_data
echo "=== Seeding Complete ==="
