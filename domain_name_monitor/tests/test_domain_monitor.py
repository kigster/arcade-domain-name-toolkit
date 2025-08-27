"""
Tests for the domain monitor application
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from domain_monitor_app import DomainMonitor
from config_loader import DomainMonitorConfig, DomainConfig, EmailRecipient


class TestDomainMonitor:
    """Tests for DomainMonitor class"""
    
    def test_init_with_config_file(self, test_yaml_config):
        """Test DomainMonitor initialization with config file"""
        with patch('domain_monitor_app.Arcade') as mock_arcade:
            monitor = DomainMonitor(test_yaml_config)
            
            assert len(monitor.domains) == 2
            assert "test-domain.com" in monitor.domains
            assert "another-test.org" in monitor.domains
            assert monitor.config.monitoring.user_id == "test@example.com"
            mock_arcade.assert_called_once()
    
    def test_init_without_config_file(self):
        """Test DomainMonitor initialization without config file"""
        with patch('domain_monitor_app.Arcade') as mock_arcade:
            with patch('domain_monitor_app.load_config') as mock_load_config:
                mock_config = DomainMonitorConfig()
                mock_config.domains = [DomainConfig(name="default.com")]
                mock_load_config.return_value = mock_config
                
                monitor = DomainMonitor()
                
                assert len(monitor.domains) == 1
                assert "default.com" in monitor.domains
                mock_load_config.assert_called_once_with(None)
    
    def test_authorize_tools_email_only(self, mock_arcade_client):
        """Test tool authorization with email notifications only"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.email.enabled = True
            monitor.config.notifications.slack.enabled = False
            
            monitor.authorize_tools()
            
            # Should authorize domain tools and Gmail
            assert mock_arcade_client.tools.authorize.call_count == 3
            expected_tools = [
                "domain_name_toolkit.check_domain_expiry",
                "domain_name_toolkit.check_ssl_expiry", 
                "Gmail.SendEmail"
            ]
            
            for call in mock_arcade_client.tools.authorize.call_args_list:
                assert call[1]['tool_name'] in expected_tools
                assert call[1]['user_id'] == monitor.config.monitoring.user_id
    
    def test_authorize_tools_email_and_slack(self, mock_arcade_client):
        """Test tool authorization with both email and Slack notifications"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.email.enabled = True
            monitor.config.notifications.slack.enabled = True
            
            monitor.authorize_tools()
            
            # Should authorize domain tools, Gmail, and Slack
            assert mock_arcade_client.tools.authorize.call_count == 4
            tool_names = [call[1]['tool_name'] for call in mock_arcade_client.tools.authorize.call_args_list]
            assert "Slack.SendMessage" in tool_names
    
    def test_authorize_tools_with_auth_required(self, mock_arcade_client):
        """Test tool authorization when additional auth is required"""
        # Mock auth response that requires user action
        mock_auth_response = Mock()
        mock_auth_response.status = "pending"
        mock_auth_response.url = "https://auth.example.com/authorize"
        mock_arcade_client.tools.authorize.return_value = mock_auth_response
        
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            
            monitor.authorize_tools()
            
            # Should wait for completion
            mock_arcade_client.auth.wait_for_completion.assert_called_with(mock_auth_response)
    
    def test_check_domain_success(self, mock_arcade_client, sample_domain_result, sample_ssl_result):
        """Test successful domain check"""
        # Mock domain check response
        domain_response = Mock()
        domain_response.output.value = sample_domain_result
        
        # Mock SSL check response
        ssl_response = Mock()
        ssl_response.output.value = sample_ssl_result
        
        mock_arcade_client.tools.execute.side_effect = [domain_response, ssl_response]
        
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            
            result = monitor.check_domain("test-domain.com")
            
            assert result["domain"] == "test-domain.com"
            assert result["domain_check"] == sample_domain_result
            assert result["ssl_check"] == sample_ssl_result
            assert "checked_at" in result
            
            # Verify both tools were called
            assert mock_arcade_client.tools.execute.call_count == 2
    
    def test_check_all_domains_success(self, mock_arcade_client, sample_domain_result, sample_ssl_result):
        """Test checking all domains successfully"""
        # Mock responses
        domain_response = Mock()
        domain_response.output.value = sample_domain_result
        ssl_response = Mock()
        ssl_response.output.value = sample_ssl_result
        mock_arcade_client.tools.execute.side_effect = [domain_response, ssl_response] * 2
        
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.domains = ["domain1.com", "domain2.com"]
            
            results = monitor.check_all_domains()
            
            assert len(results) == 2
            assert results[0]["domain"] == "domain1.com"
            assert results[1]["domain"] == "domain2.com"
            assert len(monitor.results) == 2
    
    def test_check_all_domains_with_error(self, mock_arcade_client):
        """Test checking domains when one fails"""
        # First domain succeeds
        success_response = Mock()
        success_response.output.value = {"status": "success"}
        
        # Second domain fails
        mock_arcade_client.tools.execute.side_effect = [
            success_response, success_response,  # First domain
            Exception("Network error")  # Second domain fails
        ]
        
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.domains = ["good-domain.com", "bad-domain.com"]
            
            results = monitor.check_all_domains()
            
            assert len(results) == 2
            assert results[0]["domain"] == "good-domain.com"
            assert "error" in results[1]
            assert results[1]["domain"] == "bad-domain.com"
    
    def test_get_alerts_no_expiring_domains(self):
        """Test get_alerts when no domains are expiring"""
        monitor = DomainMonitor()
        monitor.config.monitoring.alert_threshold_days = 30
        
        # Mock results with domains not expiring soon
        monitor.results = [
            {
                "domain": "safe-domain.com",
                "domain_check": {
                    "status": "success",
                    "days_until_expiry": 100,
                    "expires_soon": False
                },
                "ssl_check": {
                    "status": "success", 
                    "days_until_expiry": 90,
                    "expires_soon": False
                }
            }
        ]
        
        alerts = monitor.get_alerts()
        assert len(alerts) == 0
    
    def test_get_alerts_with_expiring_domains(self):
        """Test get_alerts when domains are expiring"""
        monitor = DomainMonitor()
        monitor.config.monitoring.alert_threshold_days = 30
        monitor.config.domains = [DomainConfig(name="expiring-domain.com")]
        
        # Mock results with expiring domain
        monitor.results = [
            {
                "domain": "expiring-domain.com",
                "domain_check": {
                    "status": "success",
                    "days_until_expiry": 15,  # Within threshold
                    "expiration_date": "2025-09-15T00:00:00+00:00",
                    "registrar": "Test Registrar"
                },
                "ssl_check": {
                    "status": "success",
                    "days_until_expiry": 10,  # Within threshold
                    "expiration_date": "2025-09-10T00:00:00+00:00"
                }
            }
        ]
        
        alerts = monitor.get_alerts()
        
        assert len(alerts) == 2  # Both domain and SSL alerts
        
        # Check domain alert
        domain_alert = next(a for a in alerts if a["type"] == "domain_registration")
        assert domain_alert["domain"] == "expiring-domain.com"
        assert domain_alert["days_until_expiry"] == 15
        assert domain_alert["registrar"] == "Test Registrar"
        assert domain_alert["threshold"] == 30
        
        # Check SSL alert
        ssl_alert = next(a for a in alerts if a["type"] == "ssl_certificate")
        assert ssl_alert["domain"] == "expiring-domain.com"
        assert ssl_alert["days_until_expiry"] == 10
        assert ssl_alert["threshold"] == 30
    
    def test_get_alerts_with_custom_threshold(self):
        """Test get_alerts with per-domain custom threshold"""
        monitor = DomainMonitor()
        monitor.config.monitoring.alert_threshold_days = 30
        monitor.config.domains = [
            DomainConfig(name="custom-domain.com", alert_threshold_days=60)  # Custom threshold
        ]
        
        # Mock results - domain expires in 45 days (within custom threshold of 60)
        monitor.results = [
            {
                "domain": "custom-domain.com",
                "domain_check": {
                    "status": "success",
                    "days_until_expiry": 45,  # Within custom threshold (60) but not global (30)
                    "expiration_date": "2025-10-15T00:00:00+00:00",
                    "registrar": "Test Registrar"
                },
                "ssl_check": {
                    "status": "success",
                    "days_until_expiry": 100  # Not expiring
                }
            }
        ]
        
        alerts = monitor.get_alerts()
        
        assert len(alerts) == 1  # Only domain alert
        assert alerts[0]["domain"] == "custom-domain.com"
        assert alerts[0]["threshold"] == 60  # Custom threshold used
    
    def test_get_alerts_ignores_error_results(self):
        """Test that get_alerts ignores results with errors"""
        monitor = DomainMonitor()
        
        monitor.results = [
            {
                "domain": "error-domain.com",
                "error": "Network timeout"
            },
            {
                "domain": "good-domain.com", 
                "domain_check": {
                    "status": "success",
                    "days_until_expiry": 100
                },
                "ssl_check": {
                    "status": "success",
                    "days_until_expiry": 100
                }
            }
        ]
        
        alerts = monitor.get_alerts()
        assert len(alerts) == 0  # Error result ignored, good domain not expiring
    
    def test_send_email_alert_disabled(self, mock_arcade_client):
        """Test send_email_alert when email notifications are disabled"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.email.enabled = False
            
            alerts = [{"domain": "test.com", "type": "domain_registration", "days_until_expiry": 10}]
            monitor.send_email_alert(alerts)
            
            # Should not call tools.execute for Gmail
            mock_arcade_client.tools.execute.assert_not_called()
    
    def test_send_email_alert_success(self, mock_arcade_client):
        """Test successful email alert sending"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.email.enabled = True
            monitor.config.notifications.email.recipients = [
                EmailRecipient(email="admin@test.com", name="Admin"),
                EmailRecipient(email="alerts@test.com", name="Alerts")
            ]
            monitor.config.notifications.email.subject_template = "Alert: {count} domains"
            
            alerts = [
                {
                    "domain": "test.com",
                    "type": "domain_registration", 
                    "days_until_expiry": 10,
                    "expiration_date": "2025-09-10T00:00:00+00:00",
                    "registrar": "Test Registrar"
                }
            ]
            
            monitor.send_email_alert(alerts)
            
            # Should send email to both recipients
            assert mock_arcade_client.tools.execute.call_count == 2
            
            # Check first email call
            first_call = mock_arcade_client.tools.execute.call_args_list[0]
            assert first_call[1]['tool_name'] == "Gmail.SendEmail"
            assert first_call[1]['input']['to'] == "admin@test.com"
            assert first_call[1]['input']['subject'] == "Alert: 1 domains"
            assert "test.com" in first_call[1]['input']['body']
            assert "Days until expiry: 10" in first_call[1]['input']['body']
    
    def test_send_slack_alert_disabled(self, mock_arcade_client):
        """Test send_slack_alert when Slack notifications are disabled"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.slack.enabled = False
            
            alerts = [{"domain": "test.com", "type": "ssl_certificate", "days_until_expiry": 5}]
            monitor.send_slack_alert(alerts)
            
            # Should not call tools.execute for Slack
            mock_arcade_client.tools.execute.assert_not_called()
    
    def test_send_slack_alert_success(self, mock_arcade_client):
        """Test successful Slack alert sending"""
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.config.notifications.slack.enabled = True
            monitor.config.notifications.slack.channel = "#test-alerts"
            monitor.config.notifications.slack.message_template = "Alert: {count} domains"
            monitor.config.notifications.slack.urgency_emojis = {
                "critical": "🔴",
                "warning": "🟡",
                "info": "ℹ️"
            }
            
            alerts = [
                {
                    "domain": "critical.com",
                    "type": "ssl_certificate",
                    "days_until_expiry": 5  # Critical (<=7 days)
                },
                {
                    "domain": "warning.com", 
                    "type": "domain_registration",
                    "days_until_expiry": 15  # Warning (8-30 days)
                }
            ]
            
            monitor.send_slack_alert(alerts)
            
            # Should send one Slack message
            assert mock_arcade_client.tools.execute.call_count == 1
            
            call = mock_arcade_client.tools.execute.call_args_list[0]
            assert call[1]['tool_name'] == "Slack.SendMessage"
            assert call[1]['input']['channel'] == "#test-alerts"
            
            message = call[1]['input']['text']
            assert "Alert: 2 domains:" in message
            assert "🔴" in message  # Critical emoji
            assert "🟡" in message  # Warning emoji
            assert "critical.com" in message
            assert "warning.com" in message
    
    def test_save_results_disabled(self):
        """Test save_results when saving is disabled"""
        monitor = DomainMonitor()
        monitor.config.monitoring.save_results = False
        monitor.results = [{"domain": "test.com"}]
        
        # Should not create any file
        monitor.save_results()
        
        # No file should be created (we can't easily test this without mocking)
        # The function should return early
    
    def test_save_results_success(self):
        """Test successful results saving"""
        monitor = DomainMonitor()
        monitor.config.monitoring.save_results = True
        monitor.config.monitoring.results_filename = "test_results.json"
        monitor.config.advanced.json_pretty_print = True
        monitor.domains = ["test1.com", "test2.com"]
        monitor.results = [
            {"domain": "test1.com", "status": "success"},
            {"domain": "test2.com", "status": "success"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            monitor.save_results(temp_file)
            
            # Verify file was created and contains expected data
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            assert "checked_at" in data
            assert "config_summary" in data
            assert data["config_summary"]["domains_monitored"] == 2
            assert len(data["results"]) == 2
            assert data["results"][0]["domain"] == "test1.com"
            
        finally:
            os.unlink(temp_file)
    
    def test_run_complete_workflow(self, mock_arcade_client):
        """Test complete run workflow"""
        # Mock successful domain checks
        domain_response = Mock()
        domain_response.output.value = {
            "status": "success", 
            "days_until_expiry": 100,
            "expires_soon": False
        }
        ssl_response = Mock()
        ssl_response.output.value = {
            "status": "success",
            "days_until_expiry": 90, 
            "expires_soon": False
        }
        mock_arcade_client.tools.execute.side_effect = [domain_response, ssl_response]
        
        with patch('domain_monitor_app.Arcade', return_value=mock_arcade_client):
            monitor = DomainMonitor()
            monitor.domains = ["test-domain.com"]
            monitor.config.monitoring.save_results = False  # Don't create files in test
            
            # Mock the output methods to avoid actual printing
            with patch('builtins.print'):
                monitor.run()
            
            # Verify workflow steps
            assert len(monitor.results) == 1
            assert monitor.results[0]["domain"] == "test-domain.com"
            
            # Verify tools were authorized (3 tools: 2 domain tools + Gmail)
            assert mock_arcade_client.tools.authorize.call_count == 3
            
            # Verify domain was checked (2 calls: domain + SSL)
            assert mock_arcade_client.tools.execute.call_count == 2