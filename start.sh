#!/usr/bin/env bash
# gunicorn core.wsgi:application --bind 0.0.0.0:$PORT

#!/usr/bin/env bash
# Activate virtual environment (Render uses .venv)
source .venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
