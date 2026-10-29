import threading
import time
import typing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from core.cache import StaleWhileRevalidateCache
from core.error_handlers import add_error_handlers
from core.exceptions import StatusUnavailable
from core.idmapper.survey_mapper import SURVEY_IDS
from status_api.models.status import DEFAULT_SINCE, SINCE_SPANS, Availability, PipelineState, Scenario
from status_api.routes import htmx
from status_api.routes.rest import router
from status_api.services import formatting, prometheus, simulation, status
from status_api.settings import BACKLOG_MIN_LAG, LAST_SEEN_LOOKBACK, PIPELINES, StatusSettings, settings

NOW = 1_800_000_000.0
DAY = 86400


@pytest.fixture(autouse=True)
def clean_cache():
    status.clear_cache()
    yield
    status.clear_cache()


def by_id(answer):
    return {p.survey: p for p in answer.pipelines}


def counts(activity):
    return activity.model_dump(mode="json")


def test_pipeline_state():
    big, small = BACKLOG_MIN_LAG, BACKLOG_MIN_LAG - 1
    recent, old = NOW - 60, NOW - 3 * DAY

    def state(lag, last_received, has_groups=True, has_topic=True):
        return status.pipeline_state(has_groups, has_topic, lag, last_received, NOW)

    assert state(big, old) == PipelineState.PROCESSING  # old backlog counts
    assert state(big, recent) == "processing"  # a StrEnum: equal to its value
    assert state(small, recent) == "up_to_date"  # stray leftovers
    assert state(0, old) == "no_data"
    assert state(0, None) == "no_data"  # the topic is reported, but nothing arrived in LAST_SEEN_LOOKBACK
    assert state(0, recent, has_groups=False) == "unknown"
    # No end offset and no last alert: the JMX exporter reports nothing, so "no alerts" would be a guess
    assert state(0, None, has_topic=False) == "unknown"
    assert state(0, recent, has_topic=False) == "up_to_date"  # what it last reported still holds
    assert state(big, None, has_topic=False) == "processing"  # the backlog is known from the lag


def test_unknown_does_not_claim_no_alerts():
    label, message = status.describe(PipelineState.UNKNOWN, 0)
    assert label == "Unknown"
    assert "No alerts" not in message and "not available" in message


def test_groups_are_assigned_to_the_right_pipeline():
    lag = {
        ("lsst-ingestion", "lsst-v11.1"): 0,
        ("features-ms", "lsst-magstats-v11.1"): 0,
        ("features-ms-ztf", "ztf-magstats-p256"): 0,
        ("stamp-step-ms-ztf", "ztf-reflector"): 0,
        ("ztf-ingestion", "ztf-reflector"): 0,
        ("sorting-hat-step", "ztf"): 0,  # legacy pipeline: not shown
        ("features-ms-reprocess", "lsst-magstats-v11"): 0,  # excluded
        ("keda-bench-1", "ztf"): 0,  # excluded
        ("someone-elses-group", "x"): 0,  # no pipeline
    }
    names = {pid: sorted(groups) for pid, groups in status.assign_groups(lag).items()}
    assert names == {
        "lsst": ["features-ms", "lsst-ingestion"],
        "ztf": ["features-ms-ztf", "stamp-step-ms-ztf", "ztf-ingestion"],
    }


def test_status_from_metrics():
    snapshot = prometheus.Snapshot(
        lag={
            ("lsst-ingestion", "lsst-v11.1"): 3_000,
            ("lsst-magstats", "lsst-correction-v11.1"): 9_000,
            ("ztf-ingestion", "ztf-reflector"): 0,
            ("ztf-magstats", "ztf-correction"): 1,
            ("sorting-hat-step", "ztf"): 50_000,  # legacy: must not make ZTF look busy
        },
        end_offsets={"lsst-v11.1": 1e9, "ztf": 1e9},
        # Every LSST topic version counts: the newest one decides.
        last_received={"lsst-v11": NOW - 5 * DAY, "lsst-v11.1": NOW - 120, "ztf": NOW - 3 * DAY},
        last_processed={"lsst-ingestion": NOW - 60},
        retention_seconds=5 * DAY,
    )
    answer = status.build_status(snapshot, [], {}, NOW)
    pipelines = by_id(answer)
    assert list(pipelines) == ["lsst", "ztf"]
    assert answer.updated_at == "2027-01-15T08:00:00+00:00"
    assert answer.history_available == "5d"
    assert answer.simulated is False

    lsst, ztf = pipelines["lsst"], pipelines["ztf"]
    assert (lsst.status, lsst.status_label) == ("processing", "Processing backlog")
    assert lsst.alerts_waiting == 12_000
    assert lsst.message.startswith("12,000 alerts are waiting")
    assert lsst.last_alert_received_at == "2027-01-15T07:58:00+00:00"
    assert lsst.last_alert_processed_at == "2027-01-15T07:59:00+00:00"

    assert ztf.status == "no_data"
    assert ztf.message == "No alerts received in the last 2 days."
    assert ztf.alerts_waiting == 1
    assert ztf.last_alert_processed_at is None


def test_pipeline_without_groups_is_unknown():
    pipelines = by_id(status.build_status(prometheus.Snapshot(), [], {}, NOW))
    assert {p.status for p in pipelines.values()} == {"unknown"}
    assert {p.status_label for p in pipelines.values()} == {"Unknown"}


def test_pipeline_without_topic_metrics_is_unknown_not_no_data():
    # The kafka exporter reports the groups, but the JMX exporter (alerts received) reports nothing
    snapshot = prometheus.Snapshot(lag={("ztf-ingestion", "ztf-reflector"): 0}, end_offsets={"lsst-v11.1": 1e9})
    ztf = by_id(status.build_status(snapshot, [], {}, NOW))["ztf"]
    assert ztf.status == "unknown"
    assert "No alerts" not in ztf.message


def test_activity_matches_topics():
    activity = prometheus.Activity(
        alerts={"lsst-v11.1": 100, "lsst-v12": 5, "ztf": 7, "ztf-reflector": 3},
        processed={"lsst-ingestion": 90, "ztf-ingestion": 0},
    )
    snapshot = prometheus.Snapshot(retention_seconds=5 * DAY)
    pipelines = by_id(status.build_status(snapshot, ["6h", "7d"], {"6h": activity}, NOW))
    # Every LSST topic version counts. ZTF alerts are counted where they arrive (`ztf`), not on the
    # internal `ztf-reflector` copy.
    assert counts(pipelines["lsst"].activity["6h"]) == {
        "availability": "available",
        "alerts_received": 105,
        "alerts_processed": 90,
    }
    assert counts(pipelines["ztf"].activity["6h"]) == {
        "availability": "available",
        "alerts_received": 7,
        "alerts_processed": 0,
    }
    assert list(pipelines["lsst"].activity) == ["6h", "7d"]  # in the order asked


def test_counts_without_metrics_are_null_not_zero():
    activity = prometheus.Activity(alerts={"ztf": 7})
    ztf = by_id(status.build_status(prometheus.Snapshot(), ["6h"], {"6h": activity}, NOW))["ztf"]
    lsst = by_id(status.build_status(prometheus.Snapshot(), ["6h"], {"6h": activity}, NOW))["lsst"]
    assert (ztf.activity["6h"].alerts_received, ztf.activity["6h"].alerts_processed) == (7, None)
    assert lsst.activity["6h"].alerts_received is None


def test_failed_counts_are_unavailable_and_long_spans_are_beyond_history():
    snapshot = prometheus.Snapshot(retention_seconds=5 * DAY)
    lsst = by_id(status.build_status(snapshot, ["6h", "7d"], {"6h": None}, NOW))["lsst"]
    assert counts(lsst.activity["6h"]) == {
        "availability": "unavailable",
        "alerts_received": None,
        "alerts_processed": None,
    }
    assert counts(lsst.activity["7d"]) == {
        "availability": "beyond_history",
        "alerts_received": None,
        "alerts_processed": None,
    }


def test_response_has_no_internal_step_names():
    snapshot = simulation.simulated_snapshot("processing", now=NOW)
    activity = {"1h": simulation.simulated_activity("1h", "processing", now=NOW)}
    text = status.build_status(snapshot, ["1h"], activity, NOW).model_dump_json()
    for groups in status.assign_groups(snapshot.lag).values():
        for name in groups:
            assert name not in text


def test_durations():
    assert formatting.duration_seconds("1h") == 3600
    assert formatting.duration_seconds("15d") == 15 * DAY
    assert formatting.duration_seconds("1d12h") == 36 * 3600
    assert formatting.human_duration(2 * DAY) == "2 days"
    assert formatting.human_duration(3600) == "1 hour"
    assert formatting.short_duration(5 * DAY) == "5d"
    assert formatting.short_duration(5400) == "90m"


@pytest.mark.parametrize("text", ["", "1.5h", "500ms", "100GiB", "1h "])
def test_a_text_that_isnt_a_whole_duration_raises(text):
    with pytest.raises(ValueError):
        formatting.duration_seconds(text)


def test_every_offered_span_and_the_no_data_window_are_durations():
    for text in [*SINCE_SPANS, status.NO_DATA_WINDOW]:
        assert formatting.duration_seconds(text) > 0


@pytest.mark.parametrize("scenario", list(simulation.FAKE_SCENARIOS))
def test_simulation_shows_each_scenario(monkeypatch, scenario):
    monkeypatch.setattr(settings, "source", "fake")
    answer = status.get_status(["1h", "7d"], scenario)
    pipelines = by_id(answer)
    assert answer.simulated is True
    assert {pid: p.status for pid, p in pipelines.items()} == simulation.FAKE_SCENARIOS[scenario]
    for p in pipelines.values():
        assert p.activity["1h"].availability == Availability.AVAILABLE
        assert p.activity["7d"].availability == Availability.BEYOND_HISTORY  # simulated Prometheus keeps 5 days
        if scenario == "unknown":
            assert p.last_alert_received_at is None and p.activity["1h"].alerts_received is None
        else:
            assert p.last_alert_received_at and p.activity["1h"].alerts_received >= 0


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def recording_prometheus(monkeypatch):
    monkeypatch.setattr(settings, "prometheus_url", "https://prometheus.example")
    monkeypatch.setattr(settings, "prometheus_user", "user")
    monkeypatch.setattr(settings, "prometheus_password", SecretStr("secret"))
    monkeypatch.setattr(settings, "kafka_exporter_instance", "kafka:9308")
    calls = []

    def fake_get(url, params=None, auth=None, timeout=None):
        query = (params or {}).get("query") or ""
        calls.append({"url": url, "query": query, "auth": auth, "timeout": timeout})
        if url.endswith("/runtimeinfo"):
            return Response({"data": {"storageRetention": "15d"}})
        if query.startswith("sum by (consumergroup, topic) (kafka_consumergroup_lag_sum"):
            result = [{"metric": {"consumergroup": "lsst-ingestion", "topic": "lsst-v11.1"}, "value": [0, "42"]}]
        elif query.startswith("max by (topic) (kafka_log_log_value"):
            result = [{"metric": {"topic": "lsst-v11.1"}, "value": [0, "123456"]}]
        elif query.startswith("max by (topic)"):
            result = [{"metric": {"topic": "lsst-v11.1"}, "value": [0, str(NOW)]}]
        elif query.startswith("max by (consumergroup)"):
            result = [{"metric": {"consumergroup": "lsst-ingestion"}, "value": [0, str(NOW + 60)]}]
        else:  # activity: alerts (by topic) or processed (by consumergroup)
            result = [
                {"metric": {"topic": "lsst-v11.1"}, "value": [0, "1000"]},
                {"metric": {"consumergroup": "lsst-ingestion"}, "value": [0, "990"]},
            ]
        return Response({"status": "success", "data": {"result": result}})

    monkeypatch.setattr(prometheus.requests, "get", fake_get)
    return calls


def check_calls(calls):
    for call in calls:
        assert call["auth"] == ("user", "secret")
        assert call["timeout"]
        # Backslashes would break the PromQL string literals.
        assert "\\" not in call["query"]


@pytest.mark.parametrize("retention, seconds", [("15d or 100GiB", 15 * DAY), ("100GiB", None)])
def test_retention_with_only_a_size_is_unknown(monkeypatch, retention, seconds):
    recording_prometheus(monkeypatch)
    monkeypatch.setattr(prometheus.requests, "get", lambda *a, **k: Response({"data": {"storageRetention": retention}}))

    assert prometheus._retention_seconds() == seconds


def test_snapshot_queries(monkeypatch):
    calls = recording_prometheus(monkeypatch)
    snapshot = prometheus.snapshot_from_prometheus()
    assert snapshot.lag == {("lsst-ingestion", "lsst-v11.1"): 42.0}
    assert snapshot.end_offsets == {"lsst-v11.1": 123456.0}
    assert snapshot.last_received == {"lsst-v11.1": NOW}
    assert snapshot.last_processed == {"lsst-ingestion": NOW + 60}
    assert snapshot.retention_seconds == 15 * DAY
    assert len(calls) == 5
    check_calls(calls)
    assert any(f"[{LAST_SEEN_LOOKBACK}:1m]" in c["query"] for c in calls)
    assert any('instance="kafka:9308"' in c["query"] for c in calls)


def test_activity_query(monkeypatch):
    calls = recording_prometheus(monkeypatch)
    activity = prometheus.activity_from_prometheus("6h")
    assert activity.alerts == {"lsst-v11.1": 1000.0}
    assert activity.processed == {"lsst-ingestion": 990.0}
    assert len(calls) == 1 and "[6h]" in calls[0]["query"]
    check_calls(calls)


def test_settings_read_the_same_environment_variables(monkeypatch):
    monkeypatch.setenv("PIPELINE_STATUS_SOURCE", " Prometheus ")
    monkeypatch.setenv("PIPELINE_STATUS_PROMETHEUS_URL", "https://prometheus.example/")
    monkeypatch.setenv("PIPELINE_STATUS_PROMETHEUS_USER", "user")
    monkeypatch.setenv("PIPELINE_STATUS_PROMETHEUS_PASSWORD", "secret")
    monkeypatch.setenv("PIPELINE_STATUS_KAFKA_EXPORTER_INSTANCE", "kafka:9308")
    monkeypatch.setenv("PIPELINE_STATUS_JMX_INSTANCE", "kafka:7071")
    monkeypatch.setenv("PIPELINE_STATUS_CACHE_SECONDS", "30")
    monkeypatch.setenv("PIPELINE_STATUS_TIMEOUT_SECONDS", "5")
    loaded = StatusSettings()
    assert loaded.source == "prometheus"
    assert loaded.prometheus_url == "https://prometheus.example"
    assert (loaded.prometheus_user, loaded.prometheus_password.get_secret_value()) == ("user", "secret")
    assert (loaded.kafka_exporter_instance, loaded.jmx_instance) == ("kafka:9308", "kafka:7071")
    assert (loaded.cache_seconds, loaded.timeout_seconds) == (30, 5)
    assert "secret" not in repr(loaded) and "secret" not in str(loaded.model_dump())


def test_settings_reject_an_unknown_source(monkeypatch):
    monkeypatch.setenv("PIPELINE_STATUS_SOURCE", "promethus")
    with pytest.raises(ValidationError):
        StatusSettings()


@pytest.mark.parametrize("value", [None, ""])
def test_settings_without_source_disable_the_api(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("PIPELINE_STATUS_SOURCE", raising=False)
    else:
        monkeypatch.setenv("PIPELINE_STATUS_SOURCE", value)
    assert StatusSettings().source is None


def client(raise_server_exceptions=True):
    app = FastAPI()
    add_error_handlers(app)
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def test_endpoint_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "source", None)
    response = client().get("/pipeline_status")
    assert response.status_code == 503
    assert response.json()["detail"] == "The status API is not configured"


def test_endpoint_fake(monkeypatch):
    monkeypatch.setattr(settings, "source", "fake")
    body = client().get("/pipeline_status?scenario=no_data&since=30m&since=24h&since=30m").json()
    assert body["simulated"] is True
    assert {p["status"] for p in body["pipelines"]} == {"no_data"}
    assert all(list(p["activity"]) == ["30m", "24h"] for p in body["pipelines"])


def test_endpoint_one_survey(monkeypatch):
    monkeypatch.setattr(settings, "source", "fake")
    body = client().get("/pipeline_status?survey_id=ZTF").json()
    assert [p["survey"] for p in body["pipelines"]] == ["ztf"]
    assert list(body["pipelines"][0]["activity"]) == DEFAULT_SINCE
    response = client().get("/pipeline_status?survey_id=atlas")
    assert response.status_code == 422  # like an unknown survey in the other APIs
    assert response.json()["detail"][0]["loc"] == ["query", "survey_id"]


def test_every_pipeline_is_a_known_survey():
    assert {p.id for p in PIPELINES} <= set(SURVEY_IDS)


@pytest.mark.parametrize("since", ["yesterday", "2h", "1h,24h", "30d"])
def test_endpoint_rejects_a_since_outside_the_offered_spans(monkeypatch, since):
    monkeypatch.setattr(settings, "source", "fake")
    response = client().get(f"/pipeline_status?since={since}")
    assert response.status_code == 422


def test_since_spans_are_the_card_windows():
    assert SINCE_SPANS == htmx.WINDOWS
    assert set(DEFAULT_SINCE) <= set(SINCE_SPANS)


def test_endpoint_hides_prometheus_errors(monkeypatch):
    monkeypatch.setattr(settings, "source", "prometheus")

    def boom():
        raise RuntimeError("401 Unauthorized for https://secret-host/")

    monkeypatch.setattr(prometheus, "snapshot_from_prometheus", boom)
    monkeypatch.setattr("core.cache.logger.exception", lambda *a, **k: None)
    response = client().get("/pipeline_status")
    assert response.status_code == 503
    assert response.json()["detail"] == "Pipeline status is temporarily unavailable"
    assert "secret-host" not in response.text


def test_scenario_is_ignored_outside_fake_mode(monkeypatch):
    monkeypatch.setattr(settings, "source", "prometheus")
    seen = {}

    def get_status(since, scenario=None):
        seen["scenario"] = scenario
        raise StatusUnavailable()

    monkeypatch.setattr("status_api.routes.rest.get_status", get_status)
    client().get("/pipeline_status?scenario=no_data")
    assert seen["scenario"] is None


def test_an_unexpected_error_is_a_500_not_an_outage(monkeypatch):
    monkeypatch.setattr(settings, "source", "prometheus")

    def bug(since, scenario=None):
        raise KeyError("a bug, not Prometheus")

    monkeypatch.setattr("status_api.routes.rest.get_status", bug)
    monkeypatch.setattr("core.error_handlers.logger.exception", lambda *a, **k: None)
    response = client(raise_server_exceptions=False).get("/pipeline_status")
    assert response.status_code == 500


def test_scenario_takes_only_the_simulated_scenarios_and_is_not_in_the_docs(monkeypatch):
    monkeypatch.setattr(settings, "source", "fake")
    assert set(typing.get_args(Scenario)) == set(simulation.FAKE_SCENARIOS)
    assert client().get("/pipeline_status?scenario=no_data").status_code == 200
    assert client().get("/pipeline_status?scenario=whatever").status_code == 422
    assert "scenario" not in client().get("/openapi.json").text


def test_docs_show_the_response_schema_and_the_since_values():
    schema = client().get("/openapi.json").json()
    ok = schema["paths"]["/pipeline_status"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert ok == {"$ref": "#/components/schemas/Status"}
    components = schema["components"]["schemas"]
    assert set(components["PipelineState"]["enum"]) == {"up_to_date", "processing", "no_data", "unknown"}
    assert set(components["Availability"]["enum"]) == {"available", "beyond_history", "unavailable"}
    assert components["Activity"]["properties"]["availability"]["description"]
    since = next(p for p in schema["paths"]["/pipeline_status"]["get"]["parameters"] if p["name"] == "since")
    assert since["schema"]["type"] == "array"
    assert since["schema"]["items"]["enum"] == SINCE_SPANS
    assert "2 days" not in schema["paths"]["/pipeline_status"]["get"]["description"]


def fake_prometheus(monkeypatch, snapshot=prometheus.Snapshot, activity=lambda since: prometheus.Activity()):
    monkeypatch.setattr(settings, "source", "prometheus")
    calls = {"snapshot": 0, "activity": []}

    def snapshot_from_prometheus():
        calls["snapshot"] += 1
        return snapshot()

    def activity_from_prometheus(since):
        calls["activity"].append(since)
        return activity(since)

    monkeypatch.setattr(prometheus, "snapshot_from_prometheus", snapshot_from_prometheus)
    monkeypatch.setattr(prometheus, "activity_from_prometheus", activity_from_prometheus)
    monkeypatch.setattr("core.cache.logger.exception", lambda *a, **k: None)
    return calls


def fail(*args):
    raise RuntimeError("down")


def test_answers_are_cached(monkeypatch):
    calls = fake_prometheus(monkeypatch)
    status.get_status(["1h", "24h"])
    status.get_status(["1h", "3d"])
    assert calls["snapshot"] == 1
    assert sorted(calls["activity"]) == ["1h", "24h", "3d"]


def test_spans_longer_than_the_history_are_not_queried(monkeypatch):
    calls = fake_prometheus(monkeypatch, snapshot=lambda: prometheus.Snapshot(retention_seconds=5 * DAY))
    answer = status.get_status(["1h", "7d"])
    assert calls["activity"] == ["1h"]
    assert by_id(answer)["lsst"].activity["7d"].availability == Availability.BEYOND_HISTORY


def test_failed_counts_dont_fail_the_status_and_are_not_beyond_history(monkeypatch):
    fake_prometheus(monkeypatch, snapshot=lambda: prometheus.Snapshot(retention_seconds=5 * DAY), activity=fail)
    answer = status.get_status(["1h"])
    assert counts(by_id(answer)["lsst"].activity["1h"]) == {
        "availability": "unavailable",
        "alerts_received": None,
        "alerts_processed": None,
    }


def test_status_unavailable_when_nothing_is_cached(monkeypatch):
    calls = fake_prometheus(monkeypatch, snapshot=fail)
    for _ in range(3):
        with pytest.raises(StatusUnavailable):
            status.get_status([])
    assert calls["snapshot"] == 1  # failures are not retried on every request


def test_the_status_caches_use_the_settings():
    assert isinstance(status.snapshots, StaleWhileRevalidateCache)
    assert status.snapshots.fresh_seconds == settings.cache_seconds
    assert status.snapshots.max_stale_seconds == settings.max_stale_seconds
    assert status.snapshots.retry_after_failure_seconds == settings.retry_after_failure_seconds
    assert status.activities.max_entries == settings.max_cache_entries


def test_requests_queued_behind_a_failed_fetch_dont_fetch_again(monkeypatch):
    def slow_fail():
        time.sleep(0.2)
        raise RuntimeError("down")

    calls = fake_prometheus(monkeypatch, snapshot=slow_fail)
    errors = []

    def request():
        try:
            status.get_status([])
        except StatusUnavailable as e:
            errors.append(e)

    threads = [threading.Thread(target=request) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert calls["snapshot"] == 1
    assert len(errors) == 5
