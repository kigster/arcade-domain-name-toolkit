"""
Tests for configuration loading functionality
"""

import tempfile
import os
import yaml
from unittest.mock import patch

from config_loader import (
    ConfigLoader,
    DomainMonitorConfig,
    DomainConfig,
    EmailRecipient,
    load_config,
)


class TestDomainConfig:
    """Tests for DomainConfig dataclass"""

    def test_domain_config_creation(self):
        """Test creating a domain configuration"""
        domain = DomainConfig(
            name="test.com", description="Test domain", alert_threshold_days=60
        )

        assert domain.name == "test.com"
        assert domain.description == "Test domain"
        assert domain.alert_threshold_days == 60

    def test_domain_config_defaults(self):
        """Test domain configuration defaults"""
        domain = DomainConfig(name="test.com")

        assert domain.name == "test.com"
        assert domain.description == ""
        assert domain.alert_threshold_days is None


class TestEmailRecipient:
    """Tests for EmailRecipient dataclass"""

    def test_email_recipient_creation(self):
        """Test creating an email recipient"""
        recipient = EmailRecipient(email="test@example.com", name="Test User")

        assert recipient.email == "test@example.com"
        assert recipient.name == "Test User"

    def test_email_recipient_defaults(self):
        """Test email recipient defaults"""
        recipient = EmailRecipient(email="test@example.com")

        assert recipient.email == "test@example.com"
        assert recipient.name == ""


class TestConfigLoader:
    """Tests for ConfigLoader class"""

    def test_load_yaml_config(self, test_yaml_config):
        """Test loading configuration from YAML file"""
        config = ConfigLoader.load_config(test_yaml_config)

        # Check monitoring config
        assert config.monitoring.alert_threshold_days == 30
        assert config.monitoring.save_results is True
        assert config.monitoring.results_filename == "test_results.json"
        assert config.monitoring.user_id == "test@example.com"

        # Check domains
        assert len(config.domains) == 2
        assert config.domains[0].name == "test-domain.com"
        assert config.domains[0].description == "Test domain"
        assert config.domains[0].alert_threshold_days == 15
        assert config.domains[1].name == "another-test.org"
        assert config.domains[1].alert_threshold_days is None

        # Check email notifications
        assert config.notifications.email.enabled is True
        assert len(config.notifications.email.recipients) == 2
        assert config.notifications.email.recipients[0].email == "admin@test.com"
        assert config.notifications.email.recipients[0].name == "Admin"
        assert (
            config.notifications.email.subject_template
            == "Test Alert - {count} domains"
        )

        # Check slack notifications
        assert config.notifications.slack.enabled is False
        assert config.notifications.slack.channel == "#test-alerts"

        # Check advanced config
        assert config.advanced.whois_timeout_seconds == 10
        assert config.advanced.ssl_timeout_seconds == 5
        assert config.advanced.max_retry_attempts == 2
        assert config.advanced.logging_level == "DEBUG"
        assert config.advanced.console_colors is False
        assert config.advanced.json_pretty_print is True

    def test_load_nonexistent_yaml_config(self):
        """Test loading non-existent YAML config falls back to defaults"""
        with patch("config_loader.ConfigLoader._load_python_config") as mock_python:
            mock_python.side_effect = ImportError("No module found")

            config = ConfigLoader.load_config("nonexistent.yaml")

            # Should load defaults
            assert isinstance(config, DomainMonitorConfig)
            assert len(config.domains) == 3  # Default domains
            assert config.domains[0].name == "google.com"

    def test_load_python_config_fallback(self):
        """Test fallback to Python configuration"""
        with patch("config_loader.ConfigLoader._load_python_config") as mock_python:
            # Mock the Python config
            mock_config = DomainMonitorConfig()
            mock_config.domains = [DomainConfig(name="python-test.com")]
            mock_python.return_value = mock_config

            # Make YAML loading fail
            config = ConfigLoader.load_config("nonexistent.yaml")

            mock_python.assert_called_once()
            assert len(config.domains) == 1
            assert config.domains[0].name == "python-test.com"

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            invalid_file = f.name

        try:
            with patch("config_loader.ConfigLoader._load_python_config") as mock_python:
                mock_python.side_effect = ImportError("No module found")

                config = ConfigLoader.load_config(invalid_file)

                # Should fall back to defaults
                assert isinstance(config, DomainMonitorConfig)
                assert len(config.domains) == 3  # Default domains
        finally:
            os.unlink(invalid_file)

    def test_save_config(self):
        """Test saving configuration to YAML file"""
        # Create a test config
        config = DomainMonitorConfig()
        config.domains = [
            DomainConfig(name="test1.com", description="Test 1"),
            DomainConfig(
                name="test2.com", description="Test 2", alert_threshold_days=45
            ),
        ]
        config.notifications.email.recipients = [
            EmailRecipient(email="test@example.com", name="Tester")
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            # Save config
            ConfigLoader.save_config(config, temp_file)

            # Load it back and verify
            loaded_config = ConfigLoader.load_config(temp_file)

            assert len(loaded_config.domains) == 2
            assert loaded_config.domains[0].name == "test1.com"
            assert loaded_config.domains[1].alert_threshold_days == 45
            assert len(loaded_config.notifications.email.recipients) == 1
            assert (
                loaded_config.notifications.email.recipients[0].email
                == "test@example.com"
            )

        finally:
            os.unlink(temp_file)

    def test_load_config_convenience_function(self, test_yaml_config):
        """Test the convenience load_config function"""
        config = load_config(test_yaml_config)

        assert isinstance(config, DomainMonitorConfig)
        assert len(config.domains) == 2
        assert config.domains[0].name == "test-domain.com"

    def test_load_config_with_missing_sections(self):
        """Test loading config with missing optional sections"""
        minimal_config = {
            "monitoring": {"user_id": "minimal@example.com"},
            "domains": [{"name": "minimal.com"}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(minimal_config, f)
            minimal_file = f.name

        try:
            config = ConfigLoader.load_config(minimal_file)

            # Should have defaults for missing sections
            assert config.monitoring.user_id == "minimal@example.com"
            assert config.monitoring.alert_threshold_days == 30  # Default
            assert len(config.domains) == 1
            assert config.domains[0].name == "minimal.com"
            assert config.notifications.email.enabled is True  # Default
            assert config.notifications.slack.enabled is False  # Default

        finally:
            os.unlink(minimal_file)

    def test_load_config_with_empty_recipients(self):
        """Test loading config with empty email recipients list"""
        config_data = {
            "monitoring": {"user_id": "test@example.com"},
            "domains": [{"name": "test.com"}],
            "notifications": {
                "email": {
                    "enabled": True,
                    "recipients": [],  # Empty list
                }
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            empty_recipients_file = f.name

        try:
            config = ConfigLoader.load_config(empty_recipients_file)

            assert config.notifications.email.enabled is True
            assert len(config.notifications.email.recipients) == 0

        finally:
            os.unlink(empty_recipients_file)
