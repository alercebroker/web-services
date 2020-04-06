FROM python:3.6


ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install gunicorn==19.9.0
RUN pip install numpy
RUN pip install -r requirements.txt
COPY /APF /APF
RUN pip install -e /APF

COPY . /app
# WORKDIR /app/scripts
EXPOSE 5000

ENV ZTF_USER=""
ENV ZTF_PASSWORD=""
ENV ZTF_HOST=""
ENV ZTF_PORT="***REMOVED***"
ENV ZTF_DATABASE=""
ENV APP_WORKERS="2"
ENV APP_BIND="0.0.0.0"
ENV APP_PORT="5000"

# CMD ["/bin/bash","entrypoint.sh"]
ENV FLASK_APP="api.app"
ENV FLASK_ENV="development"
# CMD ["flask", "run", "--host=0.0.0.0"]
WORKDIR /app/scripts
CMD ["python", "run_profile.py"]