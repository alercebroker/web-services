# Pipeline status

`GET /object_api/pipeline_status` tells users whether the data of each multisurvey pipeline (LSST, ZTF)
is current, and how many alerts arrived in the last 15 min to 7 days. The explorer shows it in its header,
and anyone can call it from their own scripts. It reads Kafka metrics from Prometheus, with fixed queries
and a 60 s cache: the browser never talks to Prometheus. The legacy ZTF pipeline is not included.

## How it decides

| state | colour | rule |
|---|---|---|
| up_to_date | green | fewer than 100 alerts waiting over all the pipeline's steps (`kafka_consumergroup_lag_sum`) |
| processing | yellow | 100 or more alerts waiting: a backlog is being processed |
| no_data | grey | nothing waiting, and no alerts received in the last 2 days |
| unknown | dark grey | no metrics for any of the pipeline's consumer groups |

A stuck pipeline shows "processing" (alerts are waiting): that is what matters to users. Which consumer
groups belong to which pipeline is in `settings.py` (`PIPELINES`).

Alert counts are the growth of the reflector topic's end offset in each window (`kafka_log_log_value`,
`name="LogEndOffset"`), the same as the Grafana panels. "Processed" is the growth of the ingestion
group's consumer offset. Windows longer than Prometheus' retention are returned as `null`. Topic
retention doesn't matter: end offsets don't go back when old messages are deleted.

Only per-pipeline totals are returned: nothing about individual steps (consumer groups) is exposed.

## Using it from a script

```sh
curl https://api-lsst.alerce.online/object_api/pipeline_status
```

```json
{"enabled": true, "updated_at": "2026-10-16T18:41:03+00:00", "no_data_window": "2d",
 "windows": ["15m", "30m", "1h", "3h", "6h", "12h", "24h", "3d", "7d"],
 "pipelines": [{"id": "lsst", "name": "LSST", "state": "processing", "lag": 9171,
                "alerts": {"15m": 106067, "1h": 424267, "7d": null},
                "processed": {"15m": 102885, "1h": 411539, "7d": null}}]}
```

- `state`: `up_to_date`, `processing`, `no_data` or `unknown` (see above). While it's `processing`, recent
  data is still coming in, so "the latest N objects" will keep changing.
- `alerts` / `processed`: alerts received and consumed by the pipeline's first step in each window.
  `null` = longer than the metrics history (Prometheus keeps 5 days today).
- Alerts are not objects: an object gets one alert per detection. To count the objects themselves, use the
  object search with a `lastmjd` filter and `count=true` (`/object_api/list_objects`).
- Refreshed at most once a minute, so polling faster gives the same answer.

## Reliability

The answer is cached for 60 s and only one request refreshes it, without making others wait: the object
API allows few requests at once per pod, so requests queueing behind a slow Prometheus would make searches
answer "busy". If Prometheus fails, it is retried after 30 s (not on every request) and the last good
answer is served for up to 10 minutes; after that the endpoint answers `503`. Errors are logged by the
API; the response never includes Prometheus' URL or error details.

## Configuration

Environment variables, in the `environment:` block of the object API in `config.yaml` (local) or its
Helm values (deployed). Never in code: this repository is public.

| variable | meaning |
|---|---|
| `PIPELINE_STATUS_SOURCE` | `prometheus`, or `fake` for simulated data. Unset: disabled (`{"enabled": false}`), and the explorer hides the badge. |
| `PIPELINE_STATUS_PROMETHEUS_URL` | Prometheus base URL |
| `PIPELINE_STATUS_PROMETHEUS_USER` / `_PASSWORD` | basic auth, if Prometheus needs it |
| `PIPELINE_STATUS_KAFKA_EXPORTER_INSTANCE` | optional `instance` label of the kafka exporter |
| `PIPELINE_STATUS_JMX_INSTANCE` | optional `instance` label of the Kafka JMX exporter |
| `PIPELINE_STATUS_CACHE_SECONDS` | default 60 |

With `PIPELINE_STATUS_SOURCE=fake`, `?scenario=mixed|processing|up_to_date|no_data` picks what the
simulation shows. The numbers move over time, so a demo looks live.

## Removing it

Delete this folder and `tests/pipeline_status/`, and the two lines marked
`pipeline status (removable)` in `object_api/api.py`. In the explorer, delete
`components/pipelineStatus.vue` and its `<pipeline-status />` line in `layouts/default.vue` and
`layouts/oid.vue`.
