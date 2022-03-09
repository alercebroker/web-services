FROM python:3.7

ADD ../../../requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install gunicorn==19.9.0
RUN pip install -r requirements.txt

COPY ADD ../../../ /app/

ENV APP_WORKERS="3"
ENV APP_THREADS="1"

