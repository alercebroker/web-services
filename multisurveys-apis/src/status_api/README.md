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
curl "https://<api host>/status_api/pipeline_status?since=30m,6h,3d"
curl "https://<api host>/status_api/pipeline_status/ztf?since=12h"   # one survey
```

```json
{
  "updated_at": "2026-10-19T15:01:39+00:00",
  "history_available": "5d",
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
        "1h": {"alerts_received": 7920, "alerts_processed": 8128},
        "24h": {"alerts_received": 217308, "alerts_processed": 217308}
      }
    }
  ]
}
```

- `status`: see below. `status_label` and `message` say the same in words, ready to show.
- `alerts_waiting`: alerts waiting to be processed, over all the pipeline's steps.
- `last_alert_received_at` / `last_alert_processed_at`: UTC, one-minute precision. `null` if there was
  none in the last 7 days (or in Prometheus' history, if shorter).
- `since`: comma-separated durations, a number and `m`, `h` or `d` (`30m`, `6h`, `3d`), at most 10 per
  request and 30 days each. A span longer than `history_available` returns `null` counts: unknown, not 0.
  If one span's counts can't be read, they come back as `null` and the rest of the answer is still given.
- Alerts are not objects: an object gets one alert per detection, and processed alerts take a few minutes
  to become searchable. To count objects, use the object search with a `lastmjd` filter and `count=true`
  (`/object_api/list_objects`).
- Errors: `422` for a bad `since` (the message says why), `404` for an unknown survey, `503` while the
  metrics can't be read (never with Prometheus' details).

The interactive docs are at `/status_api/docs`.

## How it decides

| status | rule |
|---|---|
| `up_to_date` | fewer than 100 alerts waiting over all the pipeline's steps (`kafka_consumergroup_lag_sum`) |
| `processing` | 100 or more alerts waiting: a backlog is being processed, recent data is still coming in |
| `no_data` | nothing waiting, and no alert received in the last 2 days |
| `unknown` | no metrics for any of the pipeline's consumer groups |

A stuck pipeline shows `processing` (alerts are waiting): that is what matters to users. Which consumer
groups belong to which pipeline is in `settings.py` (`PIPELINES`).

- Alerts received: growth of the survey topic's end offset in the span (`kafka_log_log_value`,
  `name="LogEndOffset"`), the same as the Grafana panels. Processed: growth of the ingestion group's
  offset. Topic retention doesn't matter: end offsets don't go back when old messages are deleted.
- Last received / processed: the last minute in which those offsets grew.

Only per-pipeline totals are returned: nothing about individual steps (consumer groups) is exposed.

## Reliability

The current state and each time span are cached for 60 s each, so many users don't turn into many
Prometheus queries. Only one request refreshes a stale answer, and the others get the previous one without
waiting: requests queueing behind a slow Prometheus would make the API answer "busy". If Prometheus fails,
it is retried after 30 s (not on every request), and the last good answer is served for up to 10 minutes;
after that the API answers `503`. Errors are logged by the API, never returned.

## Configuration

Environment variables, in the `environment:` block of `status_api` in `config.yaml` (local) or in its
Helm values (deployed). Never in code: this repository is public.

| variable | meaning |
|---|---|
| `PIPELINE_STATUS_SOURCE` | `prometheus`, or `fake` for simulated data. Unset: every request answers `503`. |
| `PIPELINE_STATUS_PROMETHEUS_URL` | Prometheus base URL |
| `PIPELINE_STATUS_PROMETHEUS_USER` / `_PASSWORD` | basic auth, if Prometheus needs it. Use a read-only user. |
| `PIPELINE_STATUS_KAFKA_EXPORTER_INSTANCE` | optional `instance` label of the kafka exporter |
| `PIPELINE_STATUS_JMX_INSTANCE` | optional `instance` label of the Kafka JMX exporter |
| `PIPELINE_STATUS_CACHE_SECONDS` | default 60 |
| `PIPELINE_STATUS_TIMEOUT_SECONDS` | timeout of each Prometheus request, default 10 |

With `PIPELINE_STATUS_SOURCE=fake`, `?scenario=mixed|processing|up_to_date|no_data` picks what the
simulation shows. The numbers move over time, so a demo looks live.

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
