"""
Test configuration and fixtures for domain monitoring tests
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock
import yaml

from config_loader import DomainMonitorConfig


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing"""
    return DomainMonitorConfig()


@pytest.fixture
def test_yaml_config():
    """Create a temporary YAML config file for testing"""
    config_data = {
        "monitoring": {
            "alert_threshold_days": 30,
            "save_results": True,
            "results_filename": "test_results.json",
            "user_id": "test@example.com",
        },
        "domains": [
            {
                "name": "test-domain.com",
                "description": "Test domain",
                "alert_threshold_days": 15,
            },
            {"name": "another-test.org", "description": "Another test domain"},
        ],
        "notifications": {
            "email": {
                "enabled": True,
                "recipients": [
                    {"email": "admin@test.com", "name": "Admin"},
                    {"email": "alerts@test.com", "name": "Alerts"},
                ],
                "subject_template": "Test Alert - {count} domains",
                "include_detailed_info": True,
            },
            "slack": {
                "enabled": False,
                "channel": "#test-alerts",
                "message_template": "Test: {count} domains expiring",
                "urgency_emojis": {"critical": "🔴", "warning": "🟡", "info": "ℹ️"},
            },
        },
        "advanced": {
            "timeouts": {"whois_timeout_seconds": 10, "ssl_timeout_seconds": 5},
            "retry": {"max_attempts": 2, "retry_delay_seconds": 1},
            "logging": {"level": "DEBUG"},
            "output": {"console_colors": False, "json_pretty_print": True},
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def mock_arcade_client():
    """Create a mock Arcade client for testing"""
    mock_client = Mock()

    # Mock tools.authorize
    mock_auth_response = Mock()
    mock_auth_response.status = "completed"
    mock_auth_response.url = "https://auth.example.com"
    mock_client.tools.authorize.return_value = mock_auth_response

    # Mock tools.execute
    mock_execute_response = Mock()
    mock_execute_response.output.value = {
        "domain": "test-domain.com",
        "status": "success",
        "expiration_date": "2025-12-31T23:59:59+00:00",
        "days_until_expiry": 100,
        "is_expired": False,
        "expires_soon": False,
    }
    mock_client.tools.execute.return_value = mock_execute_response

    # Mock auth.wait_for_completion
    mock_client.auth.wait_for_completion.return_value = None

    return mock_client


@pytest.fixture
def sample_domain_result():
    """Sample successful domain check result"""
    return {
        "domain": "test-domain.com",
        "status": "success",
        "expiration_date": "2025-12-31T23:59:59+00:00",
        "days_until_expiry": 100,
        "is_expired": False,
        "expires_soon": False,
        "registrar": "Test Registrar Inc.",
    }


@pytest.fixture
def sample_ssl_result():
    """Sample successful SSL check result"""
    return {
        "domain": "test-domain.com",
        "status": "success",
        "expiration_date": "2025-06-30T23:59:59+00:00",
        "days_until_expiry": 50,
        "is_expired": False,
        "expires_soon": False,
        "subject": [[["commonName", "test-domain.com"]]],
        "issuer": [[["commonName", "Test CA"]]],
    }


@pytest.fixture
def expiring_domain_result():
    """Sample domain result that's expiring soon"""
    return {
        "domain": "expiring-domain.com",
        "status": "success",
        "expiration_date": "2025-09-15T23:59:59+00:00",
        "days_until_expiry": 15,
        "is_expired": False,
        "expires_soon": True,
        "registrar": "Test Registrar Inc.",
    }


@pytest.fixture
def expiring_ssl_result():
    """Sample SSL result that's expiring soon"""
    return {
        "domain": "expiring-domain.com",
        "status": "success",
        "expiration_date": "2025-09-10T23:59:59+00:00",
        "days_until_expiry": 10,
        "is_expired": False,
        "expires_soon": True,
        "subject": [[["commonName", "expiring-domain.com"]]],
        "issuer": [[["commonName", "Test CA"]]],
    }


@pytest.fixture
def error_domain_result():
    """Sample domain check error result"""
    return {
        "domain": "error-domain.com",
        "status": "error",
        "message": "Domain not found",
    }


@pytest.fixture
def mock_whois_response():
    """Mock WHOIS response for testing"""
    mock_whois = Mock()
    mock_whois.expiration_date = datetime.now(timezone.utc) + timedelta(days=100)
    mock_whois.registrar = "Test Registrar Inc."
    return mock_whois


@pytest.fixture
def mock_ssl_cert():
    """Mock SSL certificate for testing"""
    future_date = datetime.now(timezone.utc) + timedelta(days=50)
    return {
        "notAfter": future_date.strftime("%b %d %H:%M:%S %Y %Z"),
        "subject": [[["commonName", "test-domain.com"]]],
        "issuer": [[["commonName", "Test CA"]]],
    }


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables"""
    os.environ["ARCADE_API_KEY"] = "test_api_key_12345"
    yield
    # Cleanup is not needed for env vars in tests
