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
- **Version.** Bump [`pyproject.toml`](pyproject.toml) (and the mirrored `version=`
  in [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py)) before every build —
  the image tag = the pyproject version, and reusing a tag affects all 8 services.

## The `root_path` / prefix-strip gotcha

The lightcurve app sets `root_path="/lightcurve_api"` (for OpenAPI docs behind the
proxy), but nginx strips that prefix, so the app receives `/static/...`, `/htmx/...`.
A Starlette `StaticFiles` **mount** resolves against the accumulated root_path and
404s on the stripped path — static files are therefore served from an explicit route
delegating to `StaticFiles.get_response`. Don't revert to `app.mount("/static", ...)`
while `root_path` is set. Full explanation in [DEPLOYMENT.md](DEPLOYMENT.md).
