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
form a group. The light curve widget can show the other objects of the viewed object's group:

- An **Associated objects** panel lists the group's members, checked, one per line. Below them, **Nearby, not
  associated** lists a few objects whose pairs scored below the threshold, unchecked and folded. The panel is
  folded when the object has no other member.
- Nothing is drawn until the user turns on **Show on the light curve**. Then the checked objects' points are
  drawn darker and translucent, with the markers of their survey and the colors of their band. Color is the
  band in every survey (ZTF g and LSST g are the same green) and the marker is the survey: detections are
  filled squares (ZTF) or circles (LSST), and forced photometry hollow triangles pointing down (ZTF) or up
  (LSST). The tooltip names each point's object.
- **Details** adds a second line under each object: the score and distance of its pair (with the member it is
  paired with, when that isn't the viewed object), and its number of detections and first and last detection
  dates, from the `object` table.
- Other objects follow the current view (Mag/Flux, Diff/Total), and a note under the switch says what to
  expect from it: in Diff, each survey and ZTF field subtracts its own template, so constant offsets between
  objects are expected (the view for transients); in Total, each survey's PSF takes in a different amount of
  host-galaxy light, so steps between surveys are expected for AGN and extended sources. Their limiting
  magnitudes aren't drawn.
- The Aladin panel marks the group's other members at their mean position, in teal, named by their survey's id.

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

- `GET /htmx/lightcurve` embeds the group (members and nearby objects) next to the object's own photometry.
  Objects are named by survey and that survey's id (`ztf:ZTF18abvkqpo`, `lsst:<diaObjectId>`), always as
  strings, because these ids don't fit in a JavaScript number.
- `GET /htmx/group_photometry?objects=ztf:<oid>,lsst:<oid>` returns the detections and forced photometry of up
  to 20 objects, each record tagged with its `oid`. The widget calls it when the group is turned on, for the
  checked objects, and again for each object checked afterwards, as it does for the ZTF data release overlay.

Code: models in `src/core/repository/association_models.py` (the tables aren't in db-plugins yet), queries in
`src/core/repository/queries/association.py`, logic in `src/lightcurve_api/services/group_service.py`, panel in
`src/lightcurve_api/routes/htmx/templates/group_panel.html.jinja`.

To see it in the Explorer, run the Explorer locally with its light curve API pointing at this API
(`LIGHTCURVE_API_BASE_URL`, e.g. `http://localhost:8001/` with the example config above) and its other API URLs at any running instance.

Not covered yet: the periodogram and download still use the viewed object only, and the association
tables are a test schema whose final layout is still under review.

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

