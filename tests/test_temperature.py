"""Tests for temperature.get_weather error handling."""
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "script")
)

import temperature


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _patch_get(monkeypatch, payload):
    monkeypatch.setattr(
        temperature.requests, "get", lambda url, **kwargs: _FakeResponse(payload)
    )


def test_default_coords_returns_na(monkeypatch):
    assert temperature.get_weather(lat="0", lon="0") == "N/A"


def test_error_payload_returns_error_string(monkeypatch):
    _patch_get(monkeypatch, {"error": True, "reason": "bad coords"})
    result = temperature.get_weather(lat="999", lon="999")
    assert isinstance(result, str) and result.startswith("Error:")


def test_non_numeric_temperature_returns_error_string(monkeypatch):
    _patch_get(monkeypatch, {"current_weather": {"temperature": "unknown"}})
    result = temperature.get_weather(lat="1", lon="1")
    assert isinstance(result, str) and result.startswith("Error:")


def test_valid_payload_returns_float(monkeypatch):
    _patch_get(monkeypatch, {"current_weather": {"temperature": 21.5}})
    assert temperature.get_weather(lat="1", lon="1") == 21.5
