FROM python:3.6

ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install gunicorn==19.9.0
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8082

ENV APP_WORKERS="3"
ENV APP_THREADS="1"

CMD ["/bin/bash","scripts/entrypoint.sh"]
