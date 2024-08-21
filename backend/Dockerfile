FROM python:3.12

SHELL ["/bin/bash", "-c"]

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
    libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim

COPY . .

RUN pip install -r requirements.txt

CMD python manage.py collectstatic --no-input \
    && gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 4 --log-level info