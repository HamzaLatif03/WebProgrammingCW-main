#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

python manage.py collectstatic --noinput
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
  python manage.py createsuperuser --noinput \
    --username "${DJANGO_SUPERUSER_USERNAME}" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || true
fi
