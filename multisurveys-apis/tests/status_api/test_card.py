"""The pipeline status card: HTML for the explorer, like the other cards, built from the same status as the JSON."""

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.error_handlers import add_error_handlers
from status_api.routes import htmx
from status_api.services import prometheus, simulation, status
from status_api.settings import settings

DOT_COLORS = {"up_to_date": "#00e676", "processing": "#ffc107", "no_data": "#9e9e9e", "unknown": "#616161"}


def card(params=""):
    app = FastAPI()
    add_error_handlers(app)
    app.include_router(htmx.router)
    return TestClient(app).get(f"/htmx/pipeline_status{params}")


@pytest.fixture(autouse=True)
def clean_cache():
    status.clear_cache()
    yield
    status.clear_cache()


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setattr(settings, "source", "fake")


def window_buttons(html):
    """{window: (enabled, selected, title)} for each window button."""
    found = {}
    for attrs, name in re.findall(r"<button([^>]*)>(\d+[mhd])</button>", html, re.S):
        disabled = re.search(r"(?<![\w:-])disabled(?![\w:-])", attrs) is not None  # the attribute, not disabled:tw-...
        title = re.search(r'title="([^"]*)"', attrs)
        found[name] = (not disabled, "tw-bg-gray-800" in attrs, title.group(1) if title else None)
    return found


def dot_color(html, survey):
    return re.search(rf'id="pipeline-{survey}".*?background: (#[0-9a-f]{{6}})', html, re.S).group(1)


@pytest.mark.parametrize("scenario", list(simulation.FAKE_SCENARIOS))
def test_card_shows_each_pipeline_with_its_status(fake, scenario):
    response = card(f"?scenario={scenario}")

    assert response.status_code == 200
    html = response.text
    assert 'id="pipeline-status-app"' in html
    for pid, state in simulation.FAKE_SCENARIOS[scenario].items():
        assert dot_color(html, pid) == DOT_COLORS[state]
    assert "Simulated data." in html


def test_unknown_card_does_not_claim_there_were_no_alerts(fake):
    html = card("?scenario=unknown").text

    assert "Unknown" in html
    assert "No alerts received" not in html
    assert "Last alert received" not in html


def test_default_window_is_selected_and_windows_beyond_the_history_are_disabled(fake):
    buttons = window_buttons(card().text)

    assert list(buttons) == htmx.WINDOWS
    assert buttons["12h"][:2] == (True, True)
    assert buttons["7d"] == (False, False, "Longer than the metrics history")  # the simulated Prometheus keeps 5 days
    assert buttons["3d"][0] is True


def test_a_window_beyond_the_history_falls_back_to_the_default(fake):
    buttons = window_buttons(card("?window=7d").text)

    assert buttons["12h"][1] is True and buttons["7d"][1] is False


def test_buttons_and_refresh_keep_the_window_and_scenario(fake):
    html = card("?window=3h&scenario=processing").text

    assert 'hx-get="http://localhost:8008/htmx/pipeline_status?window=3h&amp;scenario=processing"' in html
    assert "window=24h&amp;scenario=processing" in html  # a window button
    assert 'hx-trigger="every 60s"' in html and 'hx-select="#pipeline-status-app"' in html


def test_card_answers_503_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "source", None)

    assert card().status_code == 503


def test_card_says_when_the_status_is_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "source", "prometheus")

    def down():
        raise RuntimeError("Prometheus is down")

    monkeypatch.setattr(prometheus, "snapshot_from_prometheus", down)
    monkeypatch.setattr("core.cache.logger.exception", lambda *a, **k: None)
    response = card("?window=3h")

    assert response.status_code == 200
    assert "temporarily unavailable" in response.text
    assert 'hx-trigger="every 60s"' in response.text  # keeps trying, and recovers by itself
    assert "window=3h" in response.text
    assert "Prometheus is down" not in response.text


def test_counts_that_failed_are_temporarily_unavailable_not_beyond_the_history(monkeypatch):
    monkeypatch.setattr(settings, "source", "prometheus")

    def counts_down(since):
        raise RuntimeError("Prometheus is slow")

    snapshot = prometheus.Snapshot(lag={("ztf-ingestion", "ztf-reflector"): 0}, retention_seconds=5 * 86400)
    monkeypatch.setattr(prometheus, "snapshot_from_prometheus", lambda: snapshot)
    monkeypatch.setattr(prometheus, "activity_from_prometheus", counts_down)
    monkeypatch.setattr("core.cache.logger.exception", lambda *a, **k: None)
    html = card("?window=3h").text
    buttons = window_buttons(html)

    assert buttons["3h"][:2] == (True, True)  # still selectable: it may work on the next refresh
    assert buttons["3h"][2] == "Alert counts are temporarily unavailable"
    assert buttons["7d"] == (False, False, "Longer than the metrics history")
    assert "The alert counts for the last 3h are temporarily unavailable." in html


@pytest.mark.parametrize(
    "last_alert, expected",
    [
        ("2026-10-27T14:05:00+00:00", "14:05 UTC"),
        ("2026-10-25T14:05:00+00:00", "2026-10-25 14:05 UTC"),
        (None, None),
    ],
)
def test_last_alert_has_its_date_when_it_was_not_today(last_alert, expected):
    assert htmx._time(last_alert, "2026-10-27T20:00:00+00:00") == expected


def test_no_data_card_shows_the_date_of_the_last_alert(fake):
    html = card("?scenario=no_data").text
    assert re.search(r"Last alert received at \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", html)
