# ztf-api-apf

## Build container

`docker build -t ztf-api .`

## Run container

`docker run -it --name ztf-api -v $(pwd):/app -p 5000:5000 -e ZTF_HOST="18.211.226.219" -e ZTF_PASSWORD="ETgW4GTdR337gjP7" -e ZTF_USER="alerce" -e ZTF_DATABASE="new_pipeline" ztf-api`

## Profiling mode

Go to `settings.py` and set `PROFILE = True`

*Then, make sure you run `scripts/run_profile.py`