"""Tests for absolute timestamp parsing in the scalyr CLI script.

The CLI lives in the extensionless ``scalyr`` file at the repo root, so it
is loaded with an explicit SourceFileLoader instead of a plain import.
"""

import importlib.util
import os
from importlib.machinery import SourceFileLoader

import pytest

SCALYR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scalyr")


def load_scalyr():
    loader = SourceFileLoader("scalyr_cli_under_test", SCALYR_PATH)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


scalyr = load_scalyr()


@pytest.mark.parametrize(
    "timestamp",
    ["25am", "13pm", "9:99am", "24:00am", "12:99pm"],
)
def test_out_of_range_time_passes_through(timestamp):
    """Unparseable times are returned as-is instead of raising ValueError."""
    assert scalyr.parse_timestamp(timestamp) == timestamp


@pytest.mark.parametrize(
    "timestamp",
    ["13/45/99", "2/30/26", "0/10/2026", "13/1/2026"],
)
def test_impossible_date_passes_through(timestamp):
    """Impossible dates are returned as-is instead of raising ValueError."""
    assert scalyr.parse_timestamp(timestamp) == timestamp


def test_valid_time_still_parses():
    assert "T09:00:00" in scalyr.parse_timestamp("9am")


def test_valid_date_still_parses():
    assert scalyr.parse_timestamp("3/10/2026").startswith("2026-03-10T00:00:00")


def test_relative_time_passes_through():
    assert scalyr.parse_timestamp("4h") == "4h"
