#FROM node:14-alpine as node

#WORKDIR /app/src/main/static
#COPY src/main/static/package-lock.json .
#COPY src/main/static/package.json .
#RUN npm ci
#COPY src/main/static/ .

FROM python:3.8
ENV PYTHONBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

#COPY --from=node /app/src/main/static /app/src/main/static

#RUN python3 src/manage.py collectstatic --noinput

CMD python3 src/manage.py migrate && gunicorn target_data.wsgi --chdir src --bind 0.0.0.0 --preload --log-file -