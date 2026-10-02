# multisurveys-apis

One codebase serving several ALeRCE APIs (lightcurve, object, magstat, crossmatch,
probability, aladin, stamp, classifier). They share **one Docker image** and **one
Helm chart** ([`charts/multisurvey_api/`](../charts/multisurvey_api/)); each runs as
its own deployment in namespace `multisurvey-api-<service>` on EKS, behind an nginx
sidecar that strips the per-service path prefix before forwarding to the app.

## Build & deploy → see [DEPLOYMENT.md](DEPLOYMENT.md)

Full runbook lives in [`DEPLOYMENT.md`](DEPLOYMENT.md). The traps that cost the most
time, in short:

- **Image name.** The only deployed image is `ghcr.io/alercebroker/multisurvey-api`
  (hyphen, singular). Automated CI builds a different, unused name
  (`multisurveys-apis`); a chart comment names a third (`multisurvey_api`). To build
  the real image, name it explicitly:
  `build direct multisurvey-api --package-dir multisurveys-apis` (run from `ci_new/`,
  needs `GH_TOKEN` for the build-arg **and** `GHCR_TOKEN` for the push).
- **Deploy is manual.** `cd-multisurvey.yaml` only builds; it does not deploy, and
  `ci_new`'s deploy is broken. Deploy via `kubectl set image` + rollout (drifts from
  SSM) or the old `ci/` Helm+SSM path.
- **Version.** Bump [`pyproject.toml`](pyproject.toml) before every build — it is the only
  place that holds the version (the app reads it via [`core/version.py`](src/core/version.py)),
  the image tag = that version, and reusing a tag affects all 8 services. Locally, re-run
  `poetry install` after a bump, or the app keeps reporting the old version.

## The `root_path` / prefix-strip gotcha

The lightcurve app sets `root_path="/lightcurve_api"` (for OpenAPI docs behind the
proxy), but nginx strips that prefix, so the app receives `/static/...`, `/htmx/...`.
A Starlette `StaticFiles` **mount** resolves against the accumulated root_path and
404s on the stripped path — static files are therefore served from an explicit route
delegating to `StaticFiles.get_response`. Don't revert to `app.mount("/static", ...)`
while `root_path` is set. Full explanation in [DEPLOYMENT.md](DEPLOYMENT.md).

## Concurrency: handlers are plain `def`, and each pod caps requests

Route handlers must be plain `def`, not `async def`: they call blocking code (SQLAlchemy,
boto3, `requests`, matplotlib), and an `async def` handler that blocks freezes the whole pod.
FastAPI runs `def` handlers in a thread pool. [`core/concurrency.py`](src/core/concurrency.py)
then caps each pod at `MAX_CONCURRENT_REQUESTS` (default 5) requests in the handlers, keeping
each API within its PgBouncer connection budget. Others wait up to `QUEUE_WAIT_SECONDS`
(default 2), then get `503` + `Retry-After: 1`. Both are env vars, set per API in the
`environment:` block of its `config.yaml`. A test fails if an `async def` route reappears.

Because handlers share a process across threads: no `pyplot` (use `matplotlib.figure.Figure`),
no `boto3.client()` per request (share one, see the stamps S3 handler), and give every external
HTTP call a `timeout=`.

## Static assets go through `ASSETS_URL`

Templates reference local JS/CSS as `{{ ASSETS_URL }}/static/...` (also `htmx/`, `libraries/`,
`chart/`, `htmx-static/`), which is `<API_URL>/v/<version>`. Those paths are served with an
immutable `Cache-Control`, so each release is fetched fresh and cached forever after. Serve new
static dirs with `mount_static` from [`core/static_files.py`](src/core/static_files.py) (an
explicit route in lightcurve, because of the `root_path` gotcha above). A test fails if a
template links a local asset through `{{ API_URL }}`.

## Database sessions are AUTOCOMMIT

[`core/config/connection.py`](src/core/config/connection.py) builds the engine with
`isolation_level="AUTOCOMMIT"` and `NullPool`: each read is one round trip to the database
instead of three (no `BEGIN`/`ROLLBACK`). Writes through `ApiDatabase` (local data loading,
test fixtures) still work, but each statement commits on its own. Don't move this into
db-plugins: the pipeline uses that library and needs atomic multi-statement writes.
