# Multisurvey APIs — Build & Deploy Runbook

How the `multisurveys-apis` service is built into a container image and deployed
to the ALeRCE EKS cluster. If you only read one thing, read
[Image naming](#image-naming--read-this-first) and [Known issues](#known-issues--gotchas).

## Architecture

`multisurveys-apis` is **one codebase that serves several APIs** — lightcurve,
object, magstat, crossmatch, probability, aladin, stamp, classifier. Each runs as
its own Kubernetes deployment in its own namespace `multisurvey-api-<service>`,
but they all share **one Docker image** and **one Helm chart**
([`charts/multisurvey_api/`](../charts/multisurvey_api/)).

Request path in production:

```
AWS ALB  →  EKS  →  nginx sidecar (strips the path prefix)  →  app container (uvicorn :8000)
```

Each pod has two containers: the FastAPI app and an **nginx sidecar** whose config
comes from the chart's ConfigMap. nginx terminates the per-service path prefix:
an external request to `/<service>_api/...` is forwarded to the app as `/...`
(with `proxy_pass .../;`), and nginx sets `X-Forwarded-Prefix`.

### The `root_path` / prefix-strip gotcha (why static files 404'd)

The lightcurve app sets `root_path="/lightcurve_api"` so the OpenAPI docs and the
`servers` block resolve correctly behind the proxy. But nginx **strips**
`/lightcurve_api` before forwarding, so the app actually receives `/static/...`,
`/htmx/...`, etc.

- **Normal routes** (routers, `/docs`) match on the already-stripped path → fine.
- A Starlette **`StaticFiles` mount** resolves files against the *accumulated*
  `root_path` (`/lightcurve_api/static`), so the stripped `/static/...` that
  arrives never matches → **every asset 404s**.

Fix (in [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py)): serve static
files from an explicit route that delegates to `StaticFiles.get_response`, which
matches on the post-strip path while keeping ETag/Last-Modified, conditional
304s, Range, HEAD and traversal-safe lookups. **Do not** revert it to
`app.mount("/static", ...)` while `root_path` is set.

## Image naming — READ THIS FIRST

Three different names for one image float around the repo. **Only one is real:**

| Name | Where it appears | Is it deployed? |
|---|---|---|
| `ghcr.io/alercebroker/multisurvey-api` | live deployments (`kubectl`) | ✅ **yes — the only real one** |
| `ghcr.io/alercebroker/multisurveys-apis` | automated CI (`build_template_ms.yaml`) | ❌ wrong name, nothing pulls it |
| `ghcr.io/alercebroker/multisurvey_api` | comment in `charts/multisurvey_api/values.yaml` | ❌ not used |

The image name is the **first positional argument** to `build direct`. To build
the image production actually pulls, you **must** name it explicitly and point at
the package dir:

```
build direct multisurvey-api --package-dir multisurveys-apis
```

`build direct multisurveys-apis` (what CI runs) produces the wrong name. See
[Known issues](#known-issues--gotchas) #1.

## Versioning

- The version lives in [`pyproject.toml`](pyproject.toml) (`[tool.poetry] version`)
  and is mirrored in the FastAPI `version=` field in
  [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py). Keep them in sync.
- The build tags the image `["rc", "<pyproject version>"]` (see
  `get_tags` in [`ci_new/core/utils.py`](../ci_new/core/utils.py)). `rc` is a
  moving tag; the version tag should be treated as **immutable**.
- **Always bump `pyproject.toml` before building** so you don't overwrite a tag
  that is already deployed. All 8 services share this image, so reusing a tag can
  affect any of them on their next pull.

## Build

### Manual (the reliable path today)

Prerequisites — **two different tokens**:
- `GH_TOKEN` — build-arg, used inside the Dockerfile to clone private git deps.
- `GHCR_TOKEN` — push authentication to GHCR (as user `alerceadmin`).

Run from the `ci_new/` directory (the build resolves the repo root as `cwd/..`):

```bash
cd ci_new
export GH_TOKEN=...      # private-dep clone
export GHCR_TOKEN=...    # ghcr push auth

# sanity check first — confirm it computes tags [rc, <version>] and does NOT push
poetry run python main.py build direct multisurvey-api \
  --package-dir multisurveys-apis --build-args GH_TOKEN:$GH_TOKEN --dry-run

# real build + push
poetry run python main.py build direct multisurvey-api \
  --package-dir multisurveys-apis --build-args GH_TOKEN:$GH_TOKEN
```

- `direct` **pushes immediately** unless `--dry-run` is passed.
- `--build-args` takes `NAME:VALUE` pairs (split on the first `:`).

### Automated (build only)

[`cd-multisurvey.yaml`](../.github/workflows/cd-multisurvey.yaml) fires on push to
`main`/`staging` that touches `multisurveys-apis/**`, calling
[`build_template_ms.yaml`](../.github/workflows/build_template_ms.yaml), which runs
`build direct multisurveys-apis` in `ci_new/`.

⚠️ Two caveats: it builds the **wrongly-named** `multisurveys-apis` image, and it
**does not deploy**. Treat automated CI as "build a wrong-named image"; the real
build + deploy is manual.

## Deploy

There is **no automated deploy** for multisurvey APIs — `cd-multisurvey.yaml` only
builds. Deploy is manual.

### Quick hotfix (kubectl)

```bash
kubectl set image deploy/multisurvey-api-lightcurve \
  multisurvey-api=ghcr.io/alercebroker/multisurvey-api:<tag> \
  -n multisurvey-api-lightcurve
kubectl rollout status deploy/multisurvey-api-lightcurve -n multisurvey-api-lightcurve
```

⚠️ This is a **live override** and drifts from the Helm/SSM source of truth. The
next Helm deploy reverts it. To make it stick, also update SSM (below).

### Proper (Helm + SSM)

Per-release Helm values live in AWS SSM parameter `<release>-service-helm-values`
(fetched by [`ci_new/ssm.py`](../ci_new/ssm.py)). `image.repository`, `image.tag`,
`namespace`, and `ingress.path` all come from there. To deploy a new tag: edit the
SSM parameter's `image.tag`, then `helm upgrade` using
[`charts/multisurvey_api/`](../charts/multisurvey_api/).

The **old** `ci/` Dagger tool automates exactly this for other services
(`cd ci && poetry run python main.py deploy <pkg> production`); `ci_new`'s deploy
is currently broken (see Known issues #3).

### Services / namespaces

```bash
kubectl get ns | grep multisurvey-api
# multisurvey-api-{lightcurve,object,magstat,crossmatch,probability,aladin,stamp,classifier}

# what tag is each running?
kubectl get deploy -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.spec.template.spec.containers[*].image}{"\n"}{end}' | grep multisurvey
```

## Verify

```bash
# public (through ALB + nginx)
curl -so /dev/null -w '%{http_code}\n' https://api-lsst.alerce.online/lightcurve_api/static/lightcurve.css   # expect 200
curl -s https://api-lsst.alerce.online/lightcurve_api/openapi.json | head

# in-pod, bypassing nginx (note: app sees the STRIPPED path)
kubectl exec -n multisurvey-api-lightcurve deploy/multisurvey-api-lightcurve -c multisurvey-api -- \
  curl -so /dev/null -w '%{http_code}\n' localhost:8000/static/lightcurve.css   # expect 200 with the fix
```

## Known issues / gotchas

_As of 2026-05-30. These are documented, not yet fixed — see the table/notes if behavior surprises you._

1. **Three image names.** Automated CI builds `multisurveys-apis`; deployments pull
   `multisurvey-api`; the chart comment says `multisurvey_api`. Only `multisurvey-api`
   is real. Until unified, always build with
   `build direct multisurvey-api --package-dir multisurveys-apis`.
2. **No automated deploy.** `cd-multisurvey.yaml` only builds; deploys are manual.
3. **`ci_new` deploy is broken.** The poetry script entry is typo'd
   (`deploy = "cli.deplot:app"` in [`ci_new/pyproject.toml`](../ci_new/pyproject.toml)),
   and [`ci_new/cli/deploy.py`](../ci_new/cli/deploy.py) calls `deploy(packages, dry_run)`
   while [`ci_new/core/deploy.py`](../ci_new/core/deploy.py) expects
   `(packages, stage, dry_run)`. Use kubectl or the old `ci/` deploy.
4. **Chart-path filter mismatch.** `cd-multisurvey.yaml` watches `charts/multisurvey/**`
   but the chart dir is `charts/multisurvey_api/`, so chart-only edits don't trigger CI.
5. **Shared-tag risk.** All 8 services share the `multisurvey-api` image. Reusing or
   overwriting a tag can change any of them on their next pull. Bump `pyproject.toml`
   for a fresh, distinct tag every time.

## Reference

- Build/deploy tooling: [`ci_new/`](../ci_new/) (build works, deploy broken),
  [`ci/`](../ci/) (older Dagger pipeline, deploy works — used by other services).
- Chart: [`charts/multisurvey_api/`](../charts/multisurvey_api/) —
  `templates/deployment.yaml` (app + nginx sidecar), `templates/configmap.yaml`
  (the nginx prefix-stripping config).
- App entry: [`scripts/run_api.py`](scripts/run_api.py) (sets `API_URL` from config),
  [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py).
