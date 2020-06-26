# ztf-api-apf [![Build Status](https://travis-ci.org/alercebroker/ztf-api-new.svg?branch=master)](https://travis-ci.org/alercebroker/ztf-api-new) [![codecov](https://codecov.io/gh/alercebroker/ztf-api-new/branch/master/graph/badge.svg)](https://codecov.io/gh/alercebroker/ztf-api-new)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Build container

`docker build -t ztf-api .`

## Run container

`docker run -it --name ztf-api -v $(pwd):/app -p 5000:5000 -e ZTF_HOST="" -e ZTF_PASSWORD="" -e ZTF_USER="" -e ZTF_DATABASE="" ztf-api`

## Profiling mode

Go to `settings.py` and set `PROFILE = True`

*Then, make sure you run `scripts/run_profile.py`*
