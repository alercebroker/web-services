FROM python:3.8-slim

RUN apt update && apt install -y git


ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 5000

ENV FLASK_APP=/app/app.py

CMD ["flask","run"]
