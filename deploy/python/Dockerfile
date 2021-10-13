FROM python:3.8
ENV PYTHONBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN python3 src/manage.py collectstatic --noinput
CMD python3 src/manage.py migrate && gunicorn target_data.wsgi --chdir src --bind 0.0.0.0 --preload --log-file -