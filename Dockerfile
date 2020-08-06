FROM python:3.6

ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install gunicorn==19.9.0
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8082

ENV DB_HOST ***REMOVED***
ENV DB_DATABASE ***REMOVED***
ENV DB_USER ***REMOVED***
ENV DB_PASSWORD ***REMOVED***
ENV DB_PORT ***REMOVED***

CMD ["gunicorn", "-w", "3", "--threads", "3", "-b", "0.0.0.0:8082", "-t", "360", "api.app:create_app('settings')"]
