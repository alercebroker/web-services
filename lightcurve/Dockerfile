FROM node:22-alpine as tailwindcss_object
COPY ./lightcurve/ /lightcurve/
WORKDIR /lightcurve
RUN \
  wget -nc https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.13/tailwindcss-linux-x64 -O tailwindcss && \
  chmod +x tailwindcss && \
  ./tailwindcss -i /lightcurve/src/object_api/templates/object.css -o /compiled/object.css

FROM node:22-alpine as tailwindcss_magstats
COPY ./lightcurve/ /lightcurve/
WORKDIR /lightcurve
RUN \
  wget -nc https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.13/tailwindcss-linux-x64 -O tailwindcss && \
  chmod +x tailwindcss && \
  ./tailwindcss -i /lightcurve/src/magstats_api/templates/magstats.css -o /compiled/magstats.css

FROM node:22-alpine as tailwindcss_crossmatch
COPY ./lightcurve/ /lightcurve/
WORKDIR /lightcurve
RUN \
  wget -nc https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.13/tailwindcss-linux-x64 -O tailwindcss && \
  chmod +x tailwindcss && \
  ./tailwindcss -i /lightcurve/src/crossmatch_api/templates/crossmatch.css -o /compiled/crossmatch.css

FROM python:3.11-slim as production
RUN pip install poetry
COPY --from=builder /app /app
COPY --from=builder /libs /libs
WORKDIR /app
COPY ./lightcurve/README.md /app/README.md
COPY ./lightcurve/scripts /app/scripts
COPY ./lightcurve/src /app/src
# coing compiled main.css to each service static folder
COPY --from=tailwindcss_lightcurve /compiled/main.css /app/src/api/static
COPY --from=tailwindcss_magstats /compiled/magstats.css /app/src/magstats_api/static
COPY --from=tailwindcss_object /compiled/object.css /app/src/object_api/static
COPY --from=tailwindcss_crossmatch /compiled/crossmatch.css /app/src/crossmatch_api/static
RUN poetry install --only-root
CMD ["bash", "scripts/entrypoint.sh"]