#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python requirements
pip install -r requirements.txt

# Collect static files into STATIC_ROOT for WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
