## YAML Config file structure
The config that the apis will use to run will be defined in a yaml file in the root of the mulsituveys-apis folder.
This file will contian a list of services, one for each api the developer wish to run.

The strcuture of this file will be.

```yaml
services:
  object_api:
    source_folder: object_api
    root_path: /
    url: http://localhost:8000
    port: 8000
    env: dev
    db_config:
      psql_user: userr
      psql_password: psqw
      psql_database: db
      psql_host: host
      psql_port: 5432
      psql_schema: schema
  lightcurve_api:
    source_folder: lightcurve_api
    root_path: /
    url: http://localhost:8001
    port: 8001
    env: staging
    db_config:
      psql_user: userr
      psql_password: psqw
      psql_database: db
      psql_host: host
      psql_port: 5432
      psql_schema: schema
```


The run_all command will attempt to run all the apis that are included in the services list.

## Object groups in the light curve (demo, off by default)

The multisurvey association pipeline links objects that are the same astrophysical source, within and across
surveys. Pairs of objects get a score, and objects linked by pairs that score at least the method's threshold
form a group. Where it is enabled:

- The light curve widget lists the viewed object's group, and a few nearby objects that scored below the
  threshold, and can draw their photometry next to the object's own, on demand.
- With Fold on, the period is searched on the objects drawn. Each survey's bands are bands of their own in the
  periodogram, and when the search mixes surveys, magnitude errors below 0.03 are raised to 0.03, so LSST's very
  small errors don't outweigh ZTF's points.
- The Aladin panel marks the group's other members, and the website's results table gets an "Also seen as"
  column.

It is only enabled where `ASSOCIATION_SCHEMA` names the schema that holds the association tables. Nothing else
changes otherwise, and if the group lookup fails the widget still shows the object on its own. To try it
locally, add the variable to the light curve API's entry in `config.yaml`, and to the Aladin API's for the
markers:

```yaml
  lightcurve_api:
    environment:
      ASSOCIATION_SCHEMA: <schema with the association tables>
```

How it is served:

- `GET /htmx/lightcurve` embeds the group (members and nearby objects, one more statement) next to the object's
  own photometry.
  Objects are named by survey and that survey's id (`ztf:ZTF18abvkqpo`, `lsst:<diaObjectId>`), always as
  strings, because these ids don't fit in a JavaScript number.
- `GET /htmx/group_photometry?objects=ztf:<oid>,lsst:<oid>` returns the detections and forced photometry of up
  to 20 objects, each record tagged with its `oid`. The widget calls it when the group is turned on, for the
  checked objects, and again for each object checked afterwards, as it does for the ZTF data release overlay.
- `GET /htmx/periodogram?oid=…&survey_id=…&objects=ztf:<oid>,lsst:<oid>` searches the period on the object and
  those others (two more statements per survey).

Code: the switch in `src/core/association.py`, models in `src/core/repository/association_models.py` (the
tables aren't in db-plugins yet), queries in
`src/core/repository/queries/association.py`, logic in `src/lightcurve_api/services/group_service.py`, panel in
`src/lightcurve_api/routes/htmx/templates/group_panel.html.jinja`.

To see it in the Explorer, run the Explorer locally with its light curve API pointing at this API
(`LIGHTCURVE_API_BASE_URL`, e.g. `http://localhost:8001/` with the example config above) and its other API URLs at any running instance.

Not covered yet: the download still has the viewed object only, and the association tables are a test schema
whose final layout is still under review.

## Fold and periodogram times (BJD_TDB)

The light curve folds, and the periodogram searches, on each point's **BJD_TDB**: the time the light would have
reached the Solar System barycentre, on the TDB clock, at mid-exposure. The observed times differ by survey (ZTF
UTC at the start of the exposure, LSST TAI at mid-exposure, ZTF DR heliocentric), and Earth's orbit shifts them
by up to ±8.3 min over the year, enough to blur periods of an hour or less. The server adds `bjd_tdb` to each
detection and forced photometry record (light curve page, `/htmx/group_photometry`, `/htmx/dr_detections`); the
browser folds on it only when every point drawn has one, and keeps showing the observed MJD elsewhere.

- ZTF exposure times come from forced photometry: its own `exptime`, and for a detection the one of the forced
  photometry point of the same exposure (`pid`). Without either (older detections), 30 s is assumed.
- One position for all points, the viewed object's mean position (also for the other members of its group).
- Computed at Earth's centre with astropy's built-in ephemeris, no Earth-rotation tables needed: within about
  26 ms of the full calculation, about 55 ms per light curve. See
  [`core/periodogram/barycentric.py`](src/core/periodogram/barycentric.py).

## Colors of this project
vuetify colors:

https://vuetifyjs.com/en/styles/colors/#classes

primary: colors.blue.darken2

secondary: colors.amber.darken3

accent: colors.grey.darken3

info: colors.teal.lighten1

warning: colors.amber.base

error: colors.deepOrange.accent4

success: colors.green.accent3,

