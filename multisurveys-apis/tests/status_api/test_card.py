"""The pipeline status card: HTML for the explorer, like the other cards, built from the same status as the JSON."""

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from status_api import htmx, metrics, settings


def card(params=""):
    app = FastAPI()
    app.include_router(htmx.router)
    return TestClient(app).get(f"/htmx/pipeline_status{params}")


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "fake")


def window_buttons(html):
    """{window: (enabled, selected)} for each window button."""
    found = {}
    for attrs, name in re.findall(r"<button([^>]*)>(\d+[mhd])</button>", html, re.S):
        disabled = re.search(r"(?<![\w:-])disabled(?![\w:-])", attrs) is not None  # the attribute, not disabled:tw-...
        found[name] = (not disabled, "tw-bg-gray-800" in attrs)
    return found


def test_card_shows_each_pipeline_with_its_status(fake):
    response = card("?scenario=mixed")

    assert response.status_code == 200
    html = response.text
    assert 'id="pipeline-status-app"' in html
    for pid, state in metrics.FAKE_SCENARIOS["mixed"].items():
        assert f'id="pipeline-{pid}"' in html
        assert htmx.COLORS[state] in html
    assert "Simulated data." in html


def test_default_window_is_selected_and_windows_beyond_the_history_are_disabled(fake):
    buttons = window_buttons(card().text)

    assert list(buttons) == htmx.WINDOWS
    assert buttons["12h"] == (True, True)
    assert buttons["7d"][0] is False  # the simulated Prometheus keeps 5 days
    assert buttons["3d"][0] is True


def test_an_unavailable_window_falls_back_to_the_default(fake):
    buttons = window_buttons(card("?window=7d").text)

    assert buttons["12h"][1] is True and buttons["7d"][1] is False


def test_buttons_and_refresh_keep_the_window_and_scenario(fake):
    html = card("?window=3h&scenario=processing").text

    assert 'hx-get="http://localhost:8008/htmx/pipeline_status?window=3h&amp;scenario=processing"' in html
    assert "window=24h&amp;scenario=processing" in html  # a window button
    assert 'hx-trigger="every 60s"' in html and 'hx-select="#pipeline-status-app"' in html


def test_card_answers_503_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "SOURCE", "")

    assert card().status_code == 503
