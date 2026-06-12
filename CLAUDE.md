# web-services

Monorepo of ALeRCE web service APIs.

## What's active vs. deprecated

- **[`multisurveys-apis/`](multisurveys-apis/) is the current codebase** — one image/chart
  serving 8 APIs (lightcurve, object, magstat, crossmatch, probability, aladin, stamp,
  classifier). New work goes here. See [`multisurveys-apis/CLAUDE.md`](multisurveys-apis/CLAUDE.md).
- The standalone per-service dirs (`lightcurve/`, `astroobject/`, `xmatch-service/`,
  `periodapi/`, `tns_api/`, `alerts-api/`, `multisurvey-stamps/`, …) are the **older APIs
  being deprecated** in favor of their multisurvey versions. Don't extend them unless asked.

## Shared infra

- `charts/` — Helm charts. The active one is `charts/multisurvey_api/`.
- `ci_new/` — current build/deploy tooling. `ci/` is the old path. For deploying the
  multisurvey image (manual build + push + rollout), see
  [`multisurveys-apis/DEPLOYMENT.md`](multisurveys-apis/DEPLOYMENT.md).

## Conventions (from CI)

Python 3.11, Poetry, [`ruff`](https://docs.astral.sh/ruff/). For `multisurveys-apis/`:

- **Format & lint** (run from `multisurveys-apis/`, ruff line-length 120):
  ```sh
  ruff format --check --diff .   # CI: lint.yaml
  ruff check .
  ```
  CI lint only triggers on `multisurveys-apis/**` changes and is currently
  `continue-on-error` (won't block merge) — but match it anyway before pushing.
- **Tests** (run from the package dir, e.g. `multisurveys-apis/`):
  ```sh
  poetry run pytest -x tests --cov src
  ```
  CI (`tests.yaml`) runs pytest per-package, only when that package's files change.

## Workflow

- **Never commit directly to `main`.** Branch and open a PR (PRs target `main` or `staging`).
- **Bump the multisurvey API version before approving a PR.** The deployed image tag is
  the `pyproject.toml` version, so any PR touching `multisurveys-apis/**` must increase it
  relative to `main` — in both [`multisurveys-apis/pyproject.toml`](multisurveys-apis/pyproject.toml)
  and the mirrored `version=` in [`src/lightcurve_api/api.py`](multisurveys-apis/src/lightcurve_api/api.py).
  Reusing a tag means the deploy ships stale code (and affects all 8 services).

## Future improvements

- **Cache-bust browser-served static assets on deploy.** Any API in the repo that serves
  static front-end assets (JS/CSS) references them by a fixed filename, so browsers keep
  serving a cached copy and don't pick up a deploy until they bypass their cache — a fix can
  be live yet invisible. Append a version query (`?v={{ APP_VERSION }}`, with the deployed
  version exposed as a template/render global) to each asset reference so every release
  forces a re-fetch. The lightcurve htmx widget is the known instance today (entry
  `<script>` in `layout.html.jinja` → [`lightcurve-app.js`](multisurveys-apis/src/static/lightcurve-app.js)),
  but apply the same rule to any service that grows a static front-end. Caveat for
  ES-module entries: chained dynamic `import()`s that derive their base via
  `new URL('.', import.meta.url)` drop the query string, so sub-modules need their own
  busting if they change.
