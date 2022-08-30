FROM python:3.8-slim
ARG GITHUB_TOKEN

RUN apt update && apt install -y git
RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install gunicorn==20.1.0
RUN pip install gunicorn[gevent]
RUN pip install -r requirements.txt

COPY src .
COPY scripts .
COPY description.md .
COPY config.yml .
EXPOSE 5000

ENV APP_WORKERS="1"
ENV ENVIRONMENT="production"
ENV PROMETHEUS_MULTIPROC_DIR="/tmp"

CMD ["/bin/bash","entrypoint.sh"]
