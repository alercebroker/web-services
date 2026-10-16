import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from object_api.pipeline_status import metrics, service, settings
from object_api.pipeline_status.router import router


@pytest.fixture(autouse=True)
def clean_cache():
    service._cache.update(at=0.0, status=None, failed_at=0.0)
    yield
    service._cache.update(at=0.0, status=None, failed_at=0.0)


def by_id(status):
    return {p["id"]: p for p in status["pipelines"]}


def test_pipeline_state():
    big, small = settings.BACKLOG_MIN_LAG, settings.BACKLOG_MIN_LAG - 1
    assert service.pipeline_state(True, lag=big, recent_alerts=0) == "processing"  # old backlog still counts
    assert service.pipeline_state(True, lag=big, recent_alerts=5_000) == "processing"
    assert service.pipeline_state(True, lag=small, recent_alerts=5_000) == "up_to_date"  # stray leftovers
    assert service.pipeline_state(True, lag=0, recent_alerts=0) == "no_data"
    assert service.pipeline_state(True, lag=0, recent_alerts=None) == "up_to_date"  # window not available
    assert service.pipeline_state(False, lag=0, recent_alerts=0) == "unknown"


def test_groups_are_assigned_to_the_right_pipeline():
    raw = metrics.RawMetrics(
        lag={
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
    )
    names = {pid: sorted(groups) for pid, groups in service.assign_groups(raw).items()}
    assert names == {
        "lsst": ["features-ms", "lsst-ingestion"],
        "ztf": ["features-ms-ztf", "stamp-step-ms-ztf", "ztf-ingestion"],
    }


def test_status_from_metrics():
    raw = metrics.RawMetrics(
        lag={
            ("lsst-ingestion", "lsst-v11.1"): 3_000,
            ("lsst-magstats", "lsst-correction-v11.1"): 9_000,
            ("ztf-ingestion", "ztf-reflector"): 0,
            ("ztf-magstats", "ztf-correction"): 1,
            ("sorting-hat-step", "ztf"): 50_000,  # legacy: must not make ZTF look busy
        },
        alerts={settings.NO_DATA_WINDOW: {"lsst-v11.1": 10, "ztf": 0}},
        retention_seconds=5 * 86400,
    )
    pipelines = by_id(service.build_status(raw, source="test"))
    assert list(pipelines) == ["lsst", "ztf"]
    assert pipelines["lsst"]["state"] == "processing"
    assert pipelines["lsst"]["lag"] == 12_000
    assert pipelines["ztf"]["state"] == "no_data"
    assert pipelines["ztf"]["lag"] == 1


def test_pipeline_without_groups_is_unknown():
    pipelines = by_id(service.build_status(metrics.RawMetrics(), source="test"))
    assert {p["state"] for p in pipelines.values()} == {"unknown"}


def test_alert_counts_match_topics_and_respect_retention():
    raw = metrics.RawMetrics(
        alerts={w: {"lsst-v11.1": 100, "lsst-v12": 5, "ztf": 7, "ztf-reflector": 3} for w in settings.WINDOWS},
        processed={w: {"lsst-ingestion": 90} for w in settings.WINDOWS},
        retention_seconds=5 * 86400,
    )
    pipelines = by_id(service.build_status(raw, source="test"))
    # Every LSST topic version counts. ZTF alerts are counted where they arrive (`ztf`), not on the
    # internal `ztf-reflector` copy.
    assert pipelines["lsst"]["alerts"]["1h"] == 105
    assert pipelines["ztf"]["alerts"]["1h"] == 7
    assert pipelines["lsst"]["alerts"]["15m"] == 105
    assert pipelines["lsst"]["processed"]["3d"] == 90
    # 7 days is longer than Prometheus keeps: unavailable, not undercounted.
    assert pipelines["lsst"]["alerts"]["7d"] is None
    assert pipelines["lsst"]["processed"]["7d"] is None


def test_response_has_no_internal_step_names():
    raw = metrics.simulated("processing", now=1_000)
    text = str(service.build_status(raw, source="test"))
    for groups in service.assign_groups(raw).values():
        for name in groups:
            assert name not in text


def test_duration_seconds():
    assert metrics.duration_seconds("1h") == 3600
    assert metrics.duration_seconds("15d") == 15 * 86400
    assert metrics.duration_seconds("1d12h") == 36 * 3600
    assert metrics.duration_seconds("") is None


@pytest.mark.parametrize("scenario", list(metrics.FAKE_SCENARIOS))
def test_simulation_shows_each_scenario(scenario):
    pipelines = by_id(service.build_status(metrics.simulated(scenario, now=1_000), source="fake"))
    expected = metrics.FAKE_SCENARIOS[scenario]
    assert {pid: p["state"] for pid, p in pipelines.items()} == expected
    for p in pipelines.values():
        assert all(v >= 0 for w, v in p["alerts"].items() if w != "7d")
        assert p["alerts"]["7d"] is None  # simulated Prometheus keeps 5 days


def test_prometheus_queries(monkeypatch):
    monkeypatch.setattr(settings, "PROMETHEUS_URL", "https://prometheus.example")
    monkeypatch.setattr(settings, "PROMETHEUS_USER", "user")
    monkeypatch.setattr(settings, "PROMETHEUS_PASSWORD", "secret")
    monkeypatch.setattr(settings, "KAFKA_EXPORTER_INSTANCE", "kafka:9308")
    calls = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self.payload

    def fake_get(url, params=None, auth=None, timeout=None):
        calls.append({"url": url, "query": (params or {}).get("query"), "auth": auth, "timeout": timeout})
        if url.endswith("/runtimeinfo"):
            return Response({"data": {"storageRetention": "15d"}})
        query = params["query"]
        if query.startswith("sum by (consumergroup, topic) (kafka_consumergroup_lag_sum"):
            result = [{"metric": {"consumergroup": "lsst-ingestion", "topic": "lsst-v11.1"}, "value": [0, "42"]}]
        else:  # one query per window: alerts (by topic) or processed (by consumergroup)
            result = [
                {"metric": {"topic": "lsst-v11.1"}, "value": [0, "1000"]},
                {"metric": {"consumergroup": "lsst-ingestion"}, "value": [0, "990"]},
            ]
        return Response({"status": "success", "data": {"result": result}})

    monkeypatch.setattr(metrics.requests, "get", fake_get)
    raw = metrics.from_prometheus()

    assert raw.lag == {("lsst-ingestion", "lsst-v11.1"): 42.0}
    assert raw.alerts["1h"] == {"lsst-v11.1": 1000.0}
    assert raw.processed["24h"] == {"lsst-ingestion": 990.0}
    assert raw.retention_seconds == 15 * 86400
    assert raw.alerts[settings.NO_DATA_WINDOW] == {"lsst-v11.1": 1000.0}
    assert len(calls) == 1 + len(metrics.all_windows()) + 1
    for call in calls:
        assert call["auth"] == ("user", "secret")
        assert call["timeout"]
        # Backslashes would break the PromQL string literals.
        assert "\\" not in (call["query"] or "")
    assert any('instance="kafka:9308"' in (c["query"] or "") for c in calls)


def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_endpoint_disabled(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "")
    assert client().get("/pipeline_status").json() == {"enabled": False}


def test_endpoint_fake(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "fake")
    body = client().get("/pipeline_status?scenario=no_data").json()
    assert body["enabled"] and body["source"] == "fake"
    assert {p["state"] for p in body["pipelines"]} == {"no_data"}


def test_endpoint_hides_prometheus_errors(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")

    def boom():
        raise RuntimeError("401 Unauthorized for https://secret-host/")

    monkeypatch.setattr(metrics, "from_prometheus", boom)
    monkeypatch.setattr(service.logger, "exception", lambda *a, **k: None)
    response = client().get("/pipeline_status")
    assert response.status_code == 503
    assert "secret-host" not in response.text


def test_scenario_is_ignored_outside_fake_mode(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")
    seen = {}
    monkeypatch.setattr(service, "get_status", lambda scenario=None: seen.setdefault("scenario", scenario) or {})
    client().get("/pipeline_status?scenario=no_data")
    assert seen["scenario"] is None


def fake_prometheus(monkeypatch, behaviour):
    monkeypatch.setattr(settings, "SOURCE", "prometheus")
    calls = []

    def from_prometheus():
        calls.append(1)
        return behaviour()

    monkeypatch.setattr(metrics, "from_prometheus", from_prometheus)
    monkeypatch.setattr(service.logger, "exception", lambda *a, **k: None)
    return calls


def test_answers_are_cached(monkeypatch):
    calls = fake_prometheus(monkeypatch, metrics.RawMetrics)
    service.get_status()
    service.get_status()
    assert len(calls) == 1


def test_nobody_waits_for_a_refresh_in_progress(monkeypatch):
    calls = fake_prometheus(monkeypatch, metrics.RawMetrics)
    service.get_status()
    service._cache["at"] = 0.0 + 1  # make it old, but within MAX_STALE_SECONDS of "now" below
    monkeypatch.setattr(service.time, "time", lambda: 1 + settings.CACHE_SECONDS + 1)
    assert service._lock.acquire(blocking=False)  # another request is refreshing
    try:
        assert service.get_status()["enabled"]  # the old answer, right away
    finally:
        service._lock.release()
    assert len(calls) == 1


def test_no_cache_and_refresh_in_progress_is_unavailable(monkeypatch):
    fake_prometheus(monkeypatch, metrics.RawMetrics)
    assert service._lock.acquire(blocking=False)
    try:
        with pytest.raises(service.StatusUnavailable):
            service.get_status()
    finally:
        service._lock.release()


def test_failures_are_not_retried_on_every_request(monkeypatch):
    def fail():
        raise RuntimeError("down")

    calls = fake_prometheus(monkeypatch, fail)
    for _ in range(3):
        with pytest.raises(service.StatusUnavailable):
            service.get_status()
    assert len(calls) == 1


def test_old_answer_is_dropped_after_max_stale(monkeypatch):
    def fail():
        raise RuntimeError("down")

    fake_prometheus(monkeypatch, fail)
    service._cache.update(status={"enabled": True}, at=1.0, failed_at=0.0)
    monkeypatch.setattr(service.time, "time", lambda: 1.0 + settings.MAX_STALE_SECONDS + 1)
    with pytest.raises(service.StatusUnavailable):
        service.get_status()
