#!/bin/bash

echo "Waiting for postgres.";
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1;
done
echo "Starting api.";

echo "Applying database migrations.";
python manage.py makemigrations;
python manage.py migrate;

echo "Loading fixtures.";
python manage.py loaddata users.yaml;

# ENV variable is set and it not equal to "DEV"
if [ -n "$ENV" ] && [ "$ENV" != "DEV" ]; then
    echo "Collecting static files.";
    python manage.py collectstatic --noinput;
fi

# Execute the command passed to the Docker container
exec "$@";
