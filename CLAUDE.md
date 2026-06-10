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
- `ci_new/` — current build/deploy tooling. `ci/` is the old path.

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
