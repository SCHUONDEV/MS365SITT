"""Tests for reporter module"""

import pytest
import json
import tempfile
import os
from ms365sitt.reporter import Reporter


@pytest.fixture
def sample_results():
    """Sample check results"""
    return [
        {
            "check": "MFA Enforcement",
            "status": "PASS",
            "message": "MFA is enabled",
            "details": {"policy_count": 2},
        },
        {
            "check": "Password Policy",
            "status": "WARNING",
            "message": "Password expiry is too long",
            "details": {"validity_days": 180},
        },
        {
            "check": "Audit Logs",
            "status": "FAIL",
            "message": "Audit logs not enabled",
            "details": {},
        },
    ]


def test_reporter_init(sample_results):
    """Test Reporter initialization"""
    reporter = Reporter(sample_results)
    assert reporter.results == sample_results
    assert reporter.timestamp is not None


def test_to_console(sample_results):
    """Test console output generation"""
    reporter = Reporter(sample_results)
    output = reporter.to_console()

    assert "MFA Enforcement" in output
    assert "PASS" in output
    assert "WARNING" in output
    assert "FAIL" in output


def test_to_console_verbose(sample_results):
    """Test verbose console output"""
    reporter = Reporter(sample_results)
    output = reporter.to_console(verbose=True)

    assert "MFA Enforcement" in output
    assert "policy_count" in output or "Details" in output


def test_to_json(sample_results):
    """Test JSON output generation"""
    reporter = Reporter(sample_results)
    json_output = reporter.to_json()

    data = json.loads(json_output)
    assert "timestamp" in data
    assert "total_checks" in data
    assert data["total_checks"] == 3
    assert "summary" in data
    assert "results" in data


def test_to_json_file(sample_results):
    """Test JSON output to file"""
    reporter = Reporter(sample_results)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        filepath = f.name

    try:
        reporter.to_json(filepath)
        assert os.path.exists(filepath)

        with open(filepath, "r") as f:
            data = json.load(f)
            assert data["total_checks"] == 3
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_to_csv(sample_results):
    """Test CSV output generation"""
    reporter = Reporter(sample_results)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        filepath = f.name

    try:
        reporter.to_csv(filepath)
        assert os.path.exists(filepath)

        with open(filepath, "r") as f:
            content = f.read()
            assert "MFA Enforcement" in content
            assert "PASS" in content
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_get_summary(sample_results):
    """Test summary generation"""
    reporter = Reporter(sample_results)
    summary = reporter._get_summary()

    assert summary["PASS"] == 1
    assert summary["WARNING"] == 1
    assert summary["FAIL"] == 1
    assert summary["INFO"] == 0
    assert summary["ERROR"] == 0


def test_get_summary_text(sample_results):
    """Test summary text generation"""
    reporter = Reporter(sample_results)
    summary_text = reporter.get_summary_text()

    assert "PASS: 1" in summary_text
    assert "WARNING: 1" in summary_text
    assert "FAIL: 1" in summary_text
    assert "Total: 3" in summary_text


def test_empty_results():
    """Test reporter with empty results"""
    reporter = Reporter([])
    output = reporter.to_console()

    assert "No results" in output
