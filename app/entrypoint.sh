#!/bin/sh

set -e

echo "Running database migrations..."
python manage.py migrate --noinput

if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ] || [ "$DEBUG" = "1" ]; then
  echo "Loading dummy data from dummy_data.json..."
  python manage.py loaddata dummy_data.json
else 
  echo "Collecting static files..."
  python manage.py collectstatic --no-input
fi


echo "Starting server..."
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ] || [ "$DEBUG" = "1" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec gunicorn --bind 0.0.0.0:8000 marketplace.wsgi:application --workers 3
fi