release: python manage.py migrate --noinput && python manage.py bootstrap_admin && python manage.py seed_demo && python manage.py collectstatic --noinput
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
