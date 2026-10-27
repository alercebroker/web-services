import threading
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from status_api import metrics, service, settings
from status_api.router import router

NOW = 1_800_000_000.0
DAY = 86400


@pytest.fixture(autouse=True)
def clean_cache():
    service.clear_cache()
    yield
    service.clear_cache()


def by_id(status):
    return {p["survey"]: p for p in status["pipelines"]}


def test_pipeline_state():
    big, small = settings.BACKLOG_MIN_LAG, settings.BACKLOG_MIN_LAG - 1
    recent, old = NOW - 60, NOW - 3 * DAY
    assert service.pipeline_state(True, lag=big, last_received=old, now=NOW) == "processing"  # old backlog counts
    assert service.pipeline_state(True, lag=big, last_received=recent, now=NOW) == "processing"
    assert service.pipeline_state(True, lag=small, last_received=recent, now=NOW) == "up_to_date"  # stray leftovers
    assert service.pipeline_state(True, lag=0, last_received=old, now=NOW) == "no_data"
    assert service.pipeline_state(True, lag=0, last_received=None, now=NOW) == "no_data"  # nothing in 7 days
    assert service.pipeline_state(False, lag=0, last_received=recent, now=NOW) == "unknown"


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
    names = {pid: sorted(groups) for pid, groups in service.assign_groups(lag).items()}
    assert names == {
        "lsst": ["features-ms", "lsst-ingestion"],
        "ztf": ["features-ms-ztf", "stamp-step-ms-ztf", "ztf-ingestion"],
    }


def test_status_from_metrics():
    snapshot = metrics.Snapshot(
        lag={
            ("lsst-ingestion", "lsst-v11.1"): 3_000,
            ("lsst-magstats", "lsst-correction-v11.1"): 9_000,
            ("ztf-ingestion", "ztf-reflector"): 0,
            ("ztf-magstats", "ztf-correction"): 1,
            ("sorting-hat-step", "ztf"): 50_000,  # legacy: must not make ZTF look busy
        },
        # Every LSST topic version counts: the newest one decides.
        last_received={"lsst-v11": NOW - 5 * DAY, "lsst-v11.1": NOW - 120, "ztf": NOW - 3 * DAY},
        last_processed={"lsst-ingestion": NOW - 60},
        retention_seconds=5 * DAY,
    )
    status = service.build_status(snapshot, {}, NOW)
    pipelines = by_id(status)
    assert list(pipelines) == ["lsst", "ztf"]
    assert status["updated_at"] == "2027-01-15T08:00:00+00:00"
    assert status["history_available"] == "5d"
    assert "simulated" not in status

    lsst, ztf = pipelines["lsst"], pipelines["ztf"]
    assert (lsst["status"], lsst["status_label"]) == ("processing", "Processing backlog")
    assert lsst["alerts_waiting"] == 12_000
    assert lsst["message"].startswith("12,000 alerts are waiting")
    assert lsst["last_alert_received_at"] == "2027-01-15T07:58:00+00:00"
    assert lsst["last_alert_processed_at"] == "2027-01-15T07:59:00+00:00"

    assert ztf["status"] == "no_data"
    assert ztf["message"] == "No alerts received in the last 2 days."
    assert ztf["alerts_waiting"] == 1
    assert ztf["last_alert_processed_at"] is None


def test_pipeline_without_groups_is_unknown():
    pipelines = by_id(service.build_status(metrics.Snapshot(), {}, NOW))
    assert {p["status"] for p in pipelines.values()} == {"unknown"}
    assert {p["status_label"] for p in pipelines.values()} == {"Unknown"}


def test_activity_matches_topics():
    activity = metrics.Activity(
        alerts={"lsst-v11.1": 100, "lsst-v12": 5, "ztf": 7, "ztf-reflector": 3},
        processed={"lsst-ingestion": 90},
    )
    pipelines = by_id(service.build_status(metrics.Snapshot(), {"6h": activity, "7d": None}, NOW))
    # Every LSST topic version counts. ZTF alerts are counted where they arrive (`ztf`), not on the
    # internal `ztf-reflector` copy.
    assert pipelines["lsst"]["activity"]["6h"] == {"alerts_received": 105, "alerts_processed": 90}
    assert pipelines["ztf"]["activity"]["6h"] == {"alerts_received": 7, "alerts_processed": 0}
    # Unavailable spans are null, not zero.
    assert pipelines["lsst"]["activity"]["7d"] == {"alerts_received": None, "alerts_processed": None}
    assert list(pipelines["lsst"]["activity"]) == ["6h", "7d"]  # in the order asked


def test_response_has_no_internal_step_names():
    snapshot = metrics.simulated_snapshot("processing", now=NOW)
    activity = {"1h": metrics.simulated_activity("1h", "processing", now=NOW)}
    text = str(service.build_status(snapshot, activity, NOW))
    for groups in service.assign_groups(snapshot.lag).values():
        for name in groups:
            assert name not in text


@pytest.mark.parametrize(
    "text, expected",
    [
        (None, settings.DEFAULT_SINCE),
        ("", settings.DEFAULT_SINCE),
        ("6h", ["6h"]),
        (" 30m, 3d ,30m", ["30m", "3d"]),
    ],
)
def test_parse_since(text, expected):
    assert service.parse_since(text) == expected


@pytest.mark.parametrize(
    "text",
    ["6", "h", "0h", "1w", "-1h", "1.5h", "31d", "1h;drop", ",".join(["1h"] * 1 + [f"{n}m" for n in range(1, 11)])],
)
def test_parse_since_rejects(text):
    with pytest.raises(service.InvalidSince):
        service.parse_since(text)


def test_durations():
    assert metrics.duration_seconds("1h") == 3600
    assert metrics.duration_seconds("15d") == 15 * DAY
    assert metrics.duration_seconds("1d12h") == 36 * 3600
    assert metrics.duration_seconds("") is None
    assert service.human_duration(2 * DAY) == "2 days"
    assert service.human_duration(3600) == "1 hour"
    assert service.short_duration(5 * DAY) == "5d"
    assert service.short_duration(5400) == "90m"


@pytest.mark.parametrize("scenario", list(metrics.FAKE_SCENARIOS))
def test_simulation_shows_each_scenario(monkeypatch, scenario):
    monkeypatch.setattr(settings, "SOURCE", "fake")
    status = service.get_status(["1h", "7d"], scenario)
    pipelines = by_id(status)
    assert status["simulated"] is True
    assert {pid: p["status"] for pid, p in pipelines.items()} == metrics.FAKE_SCENARIOS[scenario]
    for p in pipelines.values():
        assert p["activity"]["1h"]["alerts_received"] >= 0
        assert p["activity"]["7d"]["alerts_received"] is None  # simulated Prometheus keeps 5 days
        assert p["last_alert_received_at"]


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def recording_prometheus(monkeypatch):
    monkeypatch.setattr(settings, "PROMETHEUS_URL", "https://prometheus.example")
    monkeypatch.setattr(settings, "PROMETHEUS_USER", "user")
    monkeypatch.setattr(settings, "PROMETHEUS_PASSWORD", "secret")
    monkeypatch.setattr(settings, "KAFKA_EXPORTER_INSTANCE", "kafka:9308")
    calls = []

    def fake_get(url, params=None, auth=None, timeout=None):
        query = (params or {}).get("query") or ""
        calls.append({"url": url, "query": query, "auth": auth, "timeout": timeout})
        if url.endswith("/runtimeinfo"):
            return Response({"data": {"storageRetention": "15d"}})
        if query.startswith("sum by (consumergroup, topic) (kafka_consumergroup_lag_sum"):
            result = [{"metric": {"consumergroup": "lsst-ingestion", "topic": "lsst-v11.1"}, "value": [0, "42"]}]
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

    monkeypatch.setattr(metrics.requests, "get", fake_get)
    return calls


def check_calls(calls):
    for call in calls:
        assert call["auth"] == ("user", "secret")
        assert call["timeout"]
        # Backslashes would break the PromQL string literals.
        assert "\\" not in call["query"]


def test_snapshot_queries(monkeypatch):
    calls = recording_prometheus(monkeypatch)
    snapshot = metrics.snapshot_from_prometheus()
    assert snapshot.lag == {("lsst-ingestion", "lsst-v11.1"): 42.0}
    assert snapshot.last_received == {"lsst-v11.1": NOW}
    assert snapshot.last_processed == {"lsst-ingestion": NOW + 60}
    assert snapshot.retention_seconds == 15 * DAY
    assert len(calls) == 4
    check_calls(calls)
    assert any(f"[{settings.LAST_SEEN_LOOKBACK}:1m]" in c["query"] for c in calls)
    assert any('instance="kafka:9308"' in c["query"] for c in calls)


def test_activity_query(monkeypatch):
    calls = recording_prometheus(monkeypatch)
    activity = metrics.activity_from_prometheus("6h")
    assert activity.alerts == {"lsst-v11.1": 1000.0}
    assert activity.processed == {"lsst-ingestion": 990.0}
    assert len(calls) == 1 and "[6h]" in calls[0]["query"]
    check_calls(calls)


def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_endpoint_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "")
    response = client().get("/pipeline_status")
    assert response.status_code == 503


def test_endpoint_fake(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "fake")
    body = client().get("/pipeline_status?scenario=no_data&since=30m,24h").json()
    assert body["simulated"] is True
    assert {p["status"] for p in body["pipelines"]} == {"no_data"}
    assert all(list(p["activity"]) == ["30m", "24h"] for p in body["pipelines"])


def test_endpoint_one_survey(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "fake")
    body = client().get("/pipeline_status/ZTF").json()
    assert body["pipeline"]["survey"] == "ztf"
    assert list(body["pipeline"]["activity"]) == settings.DEFAULT_SINCE
    assert "pipelines" not in body
    assert client().get("/pipeline_status/atlas").status_code == 404


def test_endpoint_rejects_bad_since(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "fake")
    response = client().get("/pipeline_status?since=yesterday")
    assert response.status_code == 422
    assert "yesterday" in response.json()["detail"]


def test_endpoint_hides_prometheus_errors(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")

    def boom():
        raise RuntimeError("401 Unauthorized for https://secret-host/")

    monkeypatch.setattr(metrics, "snapshot_from_prometheus", boom)
    monkeypatch.setattr(service.logger, "exception", lambda *a, **k: None)
    response = client().get("/pipeline_status")
    assert response.status_code == 503
    assert "secret-host" not in response.text


def test_scenario_is_ignored_outside_fake_mode(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")
    seen = {}
    monkeypatch.setattr(service, "get_status", lambda since, scenario=None: seen.setdefault("scenario", scenario) or {})
    client().get("/pipeline_status?scenario=no_data")
    assert seen["scenario"] is None


def fake_prometheus(monkeypatch, snapshot=metrics.Snapshot, activity=lambda since: metrics.Activity()):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")
    calls = {"snapshot": 0, "activity": []}

    def snapshot_from_prometheus():
        calls["snapshot"] += 1
        return snapshot()

    def activity_from_prometheus(since):
        calls["activity"].append(since)
        return activity(since)

    monkeypatch.setattr(metrics, "snapshot_from_prometheus", snapshot_from_prometheus)
    monkeypatch.setattr(metrics, "activity_from_prometheus", activity_from_prometheus)
    monkeypatch.setattr(service.logger, "exception", lambda *a, **k: None)
    return calls


def fail(*args):
    raise RuntimeError("down")


def test_answers_are_cached(monkeypatch):
    calls = fake_prometheus(monkeypatch)
    service.get_status(["1h", "24h"])
    service.get_status(["60m", "3d"])  # 60m is the same span as 1h
    assert calls["snapshot"] == 1
    assert sorted(calls["activity"]) == ["1h", "24h", "3d"]


def test_spans_longer_than_the_history_are_not_queried(monkeypatch):
    calls = fake_prometheus(monkeypatch, snapshot=lambda: metrics.Snapshot(retention_seconds=5 * DAY))
    status = service.get_status(["1h", "7d"])
    assert calls["activity"] == ["1h"]
    assert by_id(status)["lsst"]["activity"]["7d"]["alerts_received"] is None


def test_failed_counts_dont_fail_the_status(monkeypatch):
    fake_prometheus(monkeypatch, activity=fail)
    status = service.get_status(["1h"])
    assert by_id(status)["lsst"]["activity"]["1h"] == {"alerts_received": None, "alerts_processed": None}


def test_nobody_waits_for_a_refresh_in_progress(monkeypatch):
    calls = fake_prometheus(monkeypatch)
    service.get_status([])
    entry = service._entry("snapshot")
    entry.at = 1.0  # make it old, but within MAX_STALE_SECONDS of "now" below
    monkeypatch.setattr(service.time, "time", lambda: 1.0 + settings.CACHE_SECONDS + 1)
    assert entry.lock.acquire(blocking=False)  # another request is refreshing
    try:
        assert service.get_status([])["pipelines"]  # the old answer, right away
    finally:
        entry.lock.release()
    assert calls["snapshot"] == 1


def test_first_request_waits_for_the_one_fetching(monkeypatch):
    fake_prometheus(monkeypatch)
    monkeypatch.setattr(settings, "TIMEOUT_SECONDS", 0.05)
    entry = service._entry("snapshot")
    assert entry.lock.acquire(blocking=False)  # another request is fetching, and never finishes
    try:
        with pytest.raises(service.StatusUnavailable):
            service.get_status([])
    finally:
        entry.lock.release()


def test_failures_are_not_retried_on_every_request(monkeypatch):
    calls = fake_prometheus(monkeypatch, snapshot=fail)
    for _ in range(3):
        with pytest.raises(service.StatusUnavailable):
            service.get_status([])
    assert calls["snapshot"] == 1


def test_requests_queued_behind_a_failed_fetch_dont_fetch_again(monkeypatch):
    def slow_fail():
        time.sleep(0.2)
        raise RuntimeError("down")

    calls = fake_prometheus(monkeypatch, snapshot=slow_fail)
    errors = []

    def request():
        try:
            service.get_status([])
        except service.StatusUnavailable as e:
            errors.append(e)

    threads = [threading.Thread(target=request) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert calls["snapshot"] == 1
    assert len(errors) == 5


def test_old_answer_is_dropped_after_max_stale(monkeypatch):
    fake_prometheus(monkeypatch, snapshot=fail)
    entry = service._entry("snapshot")
    entry.value, entry.at = metrics.Snapshot(), 1.0
    monkeypatch.setattr(service.time, "time", lambda: 1.0 + settings.MAX_STALE_SECONDS + 1)
    with pytest.raises(service.StatusUnavailable):
        service.get_status([])


def test_cache_size_is_bounded(monkeypatch):
    fake_prometheus(monkeypatch)
    for minutes in range(1, service.MAX_CACHE_ENTRIES + 20):
        service.get_status([f"{minutes}m"])
    assert len(service._entries) <= service.MAX_CACHE_ENTRIES
    assert "snapshot" in service._entries


def test_an_entry_being_fetched_is_not_evicted(monkeypatch):
    fake_prometheus(monkeypatch)
    fetching = service._entry("since:60")
    assert fetching.lock.acquire(blocking=False)  # a request is fetching it, so it has no value yet (at=0)
    try:
        for minutes in range(2, service.MAX_CACHE_ENTRIES + 20):
            service.get_status([f"{minutes}m"])
        assert service._entries.get("since:60") is fetching
    finally:
        fetching.lock.release()
