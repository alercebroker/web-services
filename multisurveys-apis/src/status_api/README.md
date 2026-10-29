# Status API

Tells users whether each multisurvey pipeline (LSST, ZTF) is up to date, when it last received and
processed an alert, and how many alerts it received and processed in the time spans they ask for. The
explorer's "Pipeline status" button uses it, and anyone can call it from their own scripts.

It reads Kafka metrics from Prometheus with fixed queries, and caches the answers for 60 s. Neither the
browser nor the user talks to Prometheus, so its address and password stay on the server. It has no
database, and it is separate from the object API on purpose: a slow Prometheus can't slow down searches.
The legacy ZTF pipeline is not included.

## Using it

```sh
curl "https://<api host>/status_api/pipeline_status"                 # last 1h and 24h
curl "https://<api host>/status_api/pipeline_status?since=30m&since=6h&since=3d"
curl "https://<api host>/status_api/pipeline_status?survey_id=ztf&since=12h"   # one survey
```

```json
{
  "updated_at": "2026-10-19T15:01:39+00:00",
  "history_available": "5d",
  "simulated": false,
  "pipelines": [
    {
      "survey": "ztf",
      "name": "ZTF",
      "status": "up_to_date",
      "status_label": "Up to date",
      "message": "New alerts are processed as they arrive.",
      "alerts_waiting": 0,
      "last_alert_received_at": "2026-10-19T15:01:00+00:00",
      "last_alert_processed_at": "2026-10-19T15:00:00+00:00",
      "activity": {
        "1h": {"availability": "available", "alerts_received": 7920, "alerts_processed": 8128},
        "7d": {"availability": "beyond_history", "alerts_received": null, "alerts_processed": null}
      }
    }
  ]
}
```

- `status`: see below. `status_label` and `message` say the same in words, ready to show.
- `alerts_waiting`: alerts waiting to be processed, over all the pipeline's steps.
- `last_alert_received_at` / `last_alert_processed_at`: UTC, one-minute precision. `null` if there was
  none in the last 7 days (or in Prometheus' history, if shorter).
- `since`: repeat it for several spans (`?since=1h&since=24h`). One of `15m`, `30m`, `1h`, `3h`, `6h`,
  `12h`, `24h`, `3d`, `7d` (the card's windows); default `1h` and `24h`.
- `activity[since].availability`: `available` (the counts were read), `beyond_history` (the span is longer
  than `history_available`, so there is nothing to count) or `unavailable` (the counts couldn't be read
  right now; the rest of the answer is still given). The counts are `null` unless `available`, and also
  when there are no metrics for the survey's topic or ingestion step: unknown, not 0.
- `simulated`: `true` when the API serves simulated data.
- Alerts are not objects: an object gets one alert per detection, and processed alerts take a few minutes
  to become searchable. To count objects, use the object search with a `lastmjd` filter and `count=true`
  (`/object_api/list_objects`).
- Errors: `422` for a `since` that isn't one of the spans above or an unknown `survey_id` (like the
  other APIs), `503` while the metrics can't be read or the API is not configured (never with Prometheus'
  details).

The interactive docs are at `/status_api/docs`, with the schema of every field.

## How it decides

| status | rule |
|---|---|
| `up_to_date` | fewer than 100 alerts waiting over all the pipeline's steps (`kafka_consumergroup_lag_sum`) |
| `processing` | 100 or more alerts waiting: a backlog is being processed, recent data is still coming in |
| `no_data` | nothing waiting, and no alert received in the last 2 days, while the survey's topic is reported |
| `unknown` | no metrics for any of the pipeline's consumer groups, or (with no backlog) no end offset for the survey's topic and no alert received in the last 7 days: the JMX exporter is down or `PIPELINE_STATUS_JMX_INSTANCE` is wrong, so "no alerts" would be a guess |

A stuck pipeline shows `processing` (alerts are waiting): that is what matters to users. Which consumer
groups belong to which pipeline, and the thresholds above, are in `settings.py` (`PIPELINES`,
`BACKLOG_MIN_LAG`, `NO_DATA_WINDOW`, `LAST_SEEN_LOOKBACK`).

- Alerts received: growth of the survey topic's end offset in the span (`kafka_log_log_value`,
  `name="LogEndOffset"`), the same as the Grafana panels. Processed: growth of the ingestion group's
  offset. Topic retention doesn't matter: end offsets don't go back when old messages are deleted.
- Last received / processed: the last minute in which those offsets grew.
- Whether the survey's topic is reported at all: its current end offset.

Only per-pipeline totals are returned: nothing about individual steps (consumer groups) is exposed.

## Reliability

The current state and each time span are cached for 60 s each (`core/cache.py`), so many users don't turn into many
Prometheus queries. Only one request refreshes a stale answer, and the others get the previous one without
waiting: requests queueing behind a slow Prometheus would make the API answer "busy". If Prometheus fails,
it is retried after 30 s (not on every request), and the last good answer is served for up to 10 minutes;
after that the API answers `503`, and the card says the status is temporarily unavailable. Errors are logged
by the API, never returned.

## Configuration

Environment variables, in the `environment:` block of `status_api` in `config.yaml` (local) or in its
Helm values (deployed). Never in code: this repository is public. They are read once at startup by
`StatusSettings` in `settings.py`, which fails on an invalid value (e.g. a misspelt source).

| variable | meaning |
|---|---|
| `PIPELINE_STATUS_SOURCE` | `prometheus`, or `fake` for simulated data. Unset or empty: every request answers `503`. Anything else: the API doesn't start. |
| `PIPELINE_STATUS_PROMETHEUS_URL` | Prometheus base URL |
| `PIPELINE_STATUS_PROMETHEUS_USER` / `_PASSWORD` | basic auth, if Prometheus needs it. Use a read-only user. |
| `PIPELINE_STATUS_KAFKA_EXPORTER_INSTANCE` | optional `instance` label of the kafka exporter |
| `PIPELINE_STATUS_JMX_INSTANCE` | optional `instance` label of the Kafka JMX exporter |
| `PIPELINE_STATUS_CACHE_SECONDS` | default 60 |
| `PIPELINE_STATUS_TIMEOUT_SECONDS` | timeout of each Prometheus request, default 10 |
| `PIPELINE_STATUS_RETRY_AFTER_FAILURE_SECONDS` | after a Prometheus failure, wait this long before asking again, default 30 |
| `PIPELINE_STATUS_MAX_STALE_SECONDS` | serve the last good answer for at most this long, default 600 |
| `PIPELINE_STATUS_MAX_CACHE_ENTRIES` | most time spans cached at once, default 64 |

With `PIPELINE_STATUS_SOURCE=fake`, `?scenario=mixed|processing|up_to_date|no_data|unknown` picks what
the simulation shows (on the JSON routes and the card; it is left out of `/docs`). The numbers move over time, so a demo looks live.

## Code

Laid out like the other APIs: `routes/rest.py` (JSON), `routes/htmx.py` (the card),
`routes/parameters.py` (`since`, `survey_id`, `scenario`), `models/status.py` (response models, states, the
accepted spans), `services/status.py` (metrics -> status), `services/prometheus.py` (the queries),
`services/simulation.py` (fake data), `services/formatting.py`, and `settings.py`. Its exceptions live in
`core/exceptions.py` and are answered by `core/error_handlers.py`. The status colours are in the template.

## Running it locally

Add it to `config.yaml`. It needs no `db_config`:

```yaml
services:
  status_api:
    source_folder: status_api
    root_path: /
    url: http://localhost:8008
    port: 8008
    env: dev
    environment:
      PIPELINE_STATUS_SOURCE: fake
```

Then `poetry run status`. The explorer reads it from `STATUS_API_BASE_URL` (default
`http://127.0.0.1:8008/`).

## Deploying it

It is not deployed yet. It runs from the same image and Helm chart as the other multisurvey APIs, as a new
release: its own Helm values in SSM (with the `status_api` service and the variables above in
`configYaml`), its ingress path `/status_api`, and its name added to `API_NAMES` in
`scripts/upgrade_multisurvey_hybrid.sh`. See [DEPLOYMENT.md](../../DEPLOYMENT.md).
