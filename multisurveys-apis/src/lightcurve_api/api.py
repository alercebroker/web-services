from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from .routes.htmx import lightcurve as htmx_lightcurve
from .routes.json import conesearch, lightcurve as json_lightcurve

API_DESCRIPTION = """
Serves **lightcurves** — the time series of brightness measurements of an
astronomical object — for the surveys processed by ALeRCE.

A lightcurve is built from three complementary data products:

- **Detections**: significant (typically >5σ) flux measurements on the
  *difference image* (science image minus a reference template). Each detection
  is one alert epoch, in one band (filter).
- **Non-detections**: epochs where the object was observed but *not* detected,
  reported as the limiting magnitude (the faintest brightness that could have
  been seen). These constrain when the object was quiescent.
- **Forced photometry**: flux measured at the object's fixed position on every
  available image, whether or not it triggered a detection. Gives a uniformly
  sampled lightcurve, including faint/negative-flux epochs.

### Key concepts
- **survey_id**: the survey an object belongs to — `ztf` (Zwicky Transient
  Facility) or `lsst` (Vera C. Rubin Observatory / LSST).
- **oid**: the ALeRCE object identifier.
- **band**: the photometric filter (e.g. ZTF `g`, `r`, `i`; LSST `u g r i z y`).
- **mjd**: Modified Julian Date — the time of the observation, in days.
- **magnitude**: logarithmic brightness (smaller = brighter). Some endpoints
  also expose **flux** in nJy (linear brightness, can be negative on a
  difference image).
"""

TAGS_METADATA = [
    {
        "name": "Photometry",
        "description": "Time-series brightness measurements (detections, "
        "non-detections and forced photometry) for one or more objects.",
    },
    {
        "name": "Cone search",
        "description": "Spatial queries: find objects, or their lightcurves, "
        "near a sky position or around a given object.",
    },
    {
        "name": "Browser UI (HTMX)",
        "description": "HTML-fragment endpoints that power the ALeRCE web plots. "
        "Not intended for programmatic use — prefer the JSON endpoints above.",
    },
]

app = FastAPI(
    root_path="/lightcurve_api",
    title="ALeRCE Lightcurve API",
    version="0.2.5",
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    contact={"name": "ALeRCE", "url": "https://alerce.science"},
)
instrumentator = Instrumentator().instrument(app).expose(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(json_lightcurve.router, tags=["Photometry"])
app.include_router(conesearch.router, tags=["Cone search"])
app.include_router(htmx_lightcurve.router, tags=["Browser UI (HTMX)"])

# Static files are served via an explicit route rather than app.mount() because
# the app sets root_path="/lightcurve_api" while the nginx sidecar strips that
# prefix before forwarding. A StaticFiles *mount* resolves files against the
# accumulated root_path ("/lightcurve_api/static"), so the stripped path
# "/static/..." that actually arrives never matches and 404s. A normal route
# matches on the post-strip path (like the other routers do); delegating to
# StaticFiles.get_response keeps ETag/Last-Modified, conditional 304s, Range
# requests, HEAD and traversal-safe lookups.
_static = StaticFiles(directory="src/static")


@app.get("/static/{path:path}", name="static", include_in_schema=False)
async def static_files(path: str, request: Request):
    return await _static.get_response(path, request.scope)
