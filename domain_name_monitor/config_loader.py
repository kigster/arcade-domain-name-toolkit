#!/usr/bin/env python3

"""
Configuration loader for Domain Monitor

Loads configuration from YAML file with fallback to Python config
"""

import yaml
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DomainConfig:
    """Configuration for a single domain"""

    name: str
    description: str = ""
    alert_threshold_days: Optional[int] = None


@dataclass
class EmailRecipient:
    """Email recipient configuration"""

    email: str
    name: str = ""


@dataclass
class MonitoringConfig:
    """Main monitoring configuration"""

    alert_threshold_days: int = 30
    save_results: bool = True
    results_filename: str = "domain_check_results.json"
    user_id: str = "kig@kig.re"


@dataclass
class EmailConfig:
    """Email notification configuration"""

    enabled: bool = True
    recipients: List[EmailRecipient] = field(default_factory=list)
    subject_template: str = (
        "🚨 Domain Expiration Alert - {count} domain(s) expiring soon"
    )
    include_detailed_info: bool = True


@dataclass
class SlackConfig:
    """Slack notification configuration"""

    enabled: bool = False
    channel: str = "#alerts"
    message_template: str = "🚨 *Domain Alert* - {count} domain(s) expiring soon"
    urgency_emojis: Dict[str, str] = field(
        default_factory=lambda: {"critical": "🔴", "warning": "🟡", "info": "ℹ️"}
    )


@dataclass
class NotificationConfig:
    """Notification settings"""

    email: EmailConfig = field(default_factory=EmailConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)


@dataclass
class AdvancedConfig:
    """Advanced configuration settings"""

    whois_timeout_seconds: int = 30
    ssl_timeout_seconds: int = 10
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5
    logging_level: str = "INFO"
    console_colors: bool = True
    json_pretty_print: bool = True


@dataclass
class DomainMonitorConfig:
    """Complete domain monitor configuration"""

    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    domains: List[DomainConfig] = field(default_factory=list)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)


class ConfigLoader:
    """Configuration loader with YAML and fallback support"""

    DEFAULT_CONFIG_FILES = [
        "domain_monitor_config.yaml",
        "config.yaml",
        "domain_config.yaml",
    ]

    @classmethod
    def load_config(cls, config_file: Optional[str] = None) -> DomainMonitorConfig:
        """Load configuration from YAML file with Python fallback"""

        # Try to load YAML configuration
        if config_file:
            config_files = [config_file]
        else:
            config_files = cls.DEFAULT_CONFIG_FILES

        for yaml_file in config_files:
            if os.path.exists(yaml_file):
                try:
                    return cls._load_yaml_config(yaml_file)
                except Exception as e:
                    print(f"⚠️  Failed to load {yaml_file}: {e}")
                    continue

        # Fallback to Python configuration if available
        try:
            return cls._load_python_config()
        except ImportError:
            print("ℹ️  No configuration file found, using defaults")
            return cls._load_default_config()

    @classmethod
    def _load_yaml_config(cls, config_file: str) -> DomainMonitorConfig:
        """Load configuration from YAML file"""
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        # Parse monitoring config
        monitoring_data = data.get("monitoring", {})
        monitoring = MonitoringConfig(
            alert_threshold_days=monitoring_data.get("alert_threshold_days", 30),
            save_results=monitoring_data.get("save_results", True),
            results_filename=monitoring_data.get(
                "results_filename", "domain_check_results.json"
            ),
            user_id=monitoring_data.get("user_id", "kig@kig.re"),
        )

        # Parse domains
        domains = []
        for domain_data in data.get("domains", []):
            domains.append(
                DomainConfig(
                    name=domain_data["name"],
                    description=domain_data.get("description", ""),
                    alert_threshold_days=domain_data.get("alert_threshold_days"),
                )
            )

        # Parse notifications
        notifications_data = data.get("notifications", {})

        # Email config
        email_data = notifications_data.get("email", {})
        email_recipients = []
        for recipient_data in email_data.get("recipients", []):
            email_recipients.append(
                EmailRecipient(
                    email=recipient_data["email"], name=recipient_data.get("name", "")
                )
            )

        email_config = EmailConfig(
            enabled=email_data.get("enabled", True),
            recipients=email_recipients,
            subject_template=email_data.get(
                "subject_template",
                "🚨 Domain Expiration Alert - {count} domain(s) expiring soon",
            ),
            include_detailed_info=email_data.get("include_detailed_info", True),
        )

        # Slack config
        slack_data = notifications_data.get("slack", {})
        slack_config = SlackConfig(
            enabled=slack_data.get("enabled", False),
            channel=slack_data.get("channel", "#alerts"),
            message_template=slack_data.get(
                "message_template",
                "🚨 *Domain Alert* - {count} domain(s) expiring soon",
            ),
            urgency_emojis=slack_data.get(
                "urgency_emojis", {"critical": "🔴", "warning": "🟡", "info": "ℹ️"}
            ),
        )

        notifications = NotificationConfig(email=email_config, slack=slack_config)

        # Parse advanced config
        advanced_data = data.get("advanced", {})
        timeouts = advanced_data.get("timeouts", {})
        retry = advanced_data.get("retry", {})

        advanced = AdvancedConfig(
            whois_timeout_seconds=timeouts.get("whois_timeout_seconds", 30),
            ssl_timeout_seconds=timeouts.get("ssl_timeout_seconds", 10),
            max_retry_attempts=retry.get("max_attempts", 3),
            retry_delay_seconds=retry.get("retry_delay_seconds", 5),
            logging_level=advanced_data.get("logging", {}).get("level", "INFO"),
            console_colors=advanced_data.get("output", {}).get("console_colors", True),
            json_pretty_print=advanced_data.get("output", {}).get(
                "json_pretty_print", True
            ),
        )

        return DomainMonitorConfig(
            monitoring=monitoring,
            domains=domains,
            notifications=notifications,
            advanced=advanced,
        )

    @classmethod
    def _load_python_config(cls) -> DomainMonitorConfig:
        """Load configuration from Python config file (fallback)"""
        from domain_config import (
            DOMAINS_TO_MONITOR,
            USER_ID,
            ALERT_THRESHOLD_DAYS,
            ENABLE_EMAIL_ALERTS,
            EMAIL_RECIPIENTS,
            ENABLE_SLACK_ALERTS,
            SLACK_CHANNEL,
            SAVE_RESULTS_TO_FILE,
            RESULTS_FILENAME,
        )

        # Convert Python config to our data structures
        domains = [DomainConfig(name=domain) for domain in DOMAINS_TO_MONITOR]

        email_recipients = [EmailRecipient(email=email) for email in EMAIL_RECIPIENTS]
        email_config = EmailConfig(
            enabled=ENABLE_EMAIL_ALERTS, recipients=email_recipients
        )

        slack_config = SlackConfig(enabled=ENABLE_SLACK_ALERTS, channel=SLACK_CHANNEL)

        monitoring = MonitoringConfig(
            alert_threshold_days=ALERT_THRESHOLD_DAYS,
            save_results=SAVE_RESULTS_TO_FILE,
            results_filename=RESULTS_FILENAME,
            user_id=USER_ID,
        )

        return DomainMonitorConfig(
            monitoring=monitoring,
            domains=domains,
            notifications=NotificationConfig(email=email_config, slack=slack_config),
        )

    @classmethod
    def _load_default_config(cls) -> DomainMonitorConfig:
        """Load default configuration"""
        domains = [
            DomainConfig(name="google.com", description="Google's main domain"),
            DomainConfig(name="github.com", description="GitHub platform"),
            DomainConfig(name="example.com", description="Example domain"),
        ]

        email_recipients = [EmailRecipient(email="kig@kig.re", name="Admin")]

        return DomainMonitorConfig(
            domains=domains,
            notifications=NotificationConfig(
                email=EmailConfig(recipients=email_recipients)
            ),
        )

    @classmethod
    def save_config(
        cls, config: DomainMonitorConfig, filename: str = "domain_monitor_config.yaml"
    ):
        """Save configuration to YAML file"""

        # Convert config to dictionary
        data = {
            "monitoring": {
                "alert_threshold_days": config.monitoring.alert_threshold_days,
                "save_results": config.monitoring.save_results,
                "results_filename": config.monitoring.results_filename,
                "user_id": config.monitoring.user_id,
            },
            "domains": [
                {
                    "name": domain.name,
                    "description": domain.description,
                    **(
                        {"alert_threshold_days": domain.alert_threshold_days}
                        if domain.alert_threshold_days
                        else {}
                    ),
                }
                for domain in config.domains
            ],
            "notifications": {
                "email": {
                    "enabled": config.notifications.email.enabled,
                    "recipients": [
                        {"email": r.email, "name": r.name}
                        for r in config.notifications.email.recipients
                    ],
                    "subject_template": config.notifications.email.subject_template,
                    "include_detailed_info": config.notifications.email.include_detailed_info,
                },
                "slack": {
                    "enabled": config.notifications.slack.enabled,
                    "channel": config.notifications.slack.channel,
                    "message_template": config.notifications.slack.message_template,
                    "urgency_emojis": config.notifications.slack.urgency_emojis,
                },
            },
            "advanced": {
                "timeouts": {
                    "whois_timeout_seconds": config.advanced.whois_timeout_seconds,
                    "ssl_timeout_seconds": config.advanced.ssl_timeout_seconds,
                },
                "retry": {
                    "max_attempts": config.advanced.max_retry_attempts,
                    "retry_delay_seconds": config.advanced.retry_delay_seconds,
                },
                "logging": {"level": config.advanced.logging_level},
                "output": {
                    "console_colors": config.advanced.console_colors,
                    "json_pretty_print": config.advanced.json_pretty_print,
                },
            },
        }

        with open(filename, "w") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)

        print(f"Configuration saved to {filename}")


def load_config(config_file: Optional[str] = None) -> DomainMonitorConfig:
    """Convenience function to load configuration"""
    return ConfigLoader.load_config(config_file)


if __name__ == "__main__":
    # Test configuration loading
    config = load_config()
    print(f"Loaded config with {len(config.domains)} domains")
    for domain in config.domains:
        print(f"  - {domain.name}: {domain.description}")
