# ztf-api-apf

## Build container

`docker build -t ztf-api .`

## Run container

`docker run -it --name ztf-api -v $(pwd):/app -p 5000:5000 -e ZTF_HOST="" -e ZTF_PASSWORD="" -e ZTF_USER="" -e ZTF_DATABASE="" ztf-api`

## Profiling mode

Go to `settings.py` and set `PROFILE = True`

*Then, make sure you run `scripts/run_profile.py`*
