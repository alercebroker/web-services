FROM python:3.6

ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install gunicorn==19.9.0
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8082

ENV DB_HOST 13.58.88.2
ENV DB_DATABASE new_pipeline_ts
ENV DB_USER alerceapi
ENV DB_PASSWORD api2020
ENV DB_PORT 5432

CMD ["gunicorn", "-w", "3", "--threads", "3", "-b", "0.0.0.0:8082", "-t", "360", "api.app:create_app('settings')"]
