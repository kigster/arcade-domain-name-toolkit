#!/usr/bin/env python3

"""
Domain Monitor Application

Monitors a list of domains for expiration (both domain registration and SSL certificates)
and sends alerts via Gmail and Slack when domains are expiring within 30 days.
"""

import json
import os
from typing import List, Dict
from arcadepy import Arcade
from datetime import datetime
from config_loader import load_config, DomainMonitorConfig


class DomainMonitor:
    def __init__(self, config_file: str = None):
        self.client = Arcade()
        self.results = []
        self.config = load_config(config_file)
        self.domains = [domain.name for domain in self.config.domains]
        
    def authorize_tools(self):
        """Authorize all required tools."""
        tools_to_authorize = [
            "domain_name_toolkit.check_domain_expiry",
            "domain_name_toolkit.check_ssl_expiry", 
            "Gmail.SendEmail"
        ]
        
        # Add Slack if enabled
        if self.config.notifications.slack.enabled:
            tools_to_authorize.append("Slack.SendMessage")
        
        for tool_name in tools_to_authorize:
            print(f"Authorizing {tool_name}...")
            auth_response = self.client.tools.authorize(
                tool_name=tool_name,
                user_id=self.config.monitoring.user_id,
            )
            
            if auth_response.status != "completed":
                print(f"Click this link to authorize {tool_name}: {auth_response.url}")
                self.client.auth.wait_for_completion(auth_response)
                print(f"✅ {tool_name} authorized")
    
    def check_domain(self, domain: str) -> Dict:
        """Check both domain registration and SSL certificate expiry for a domain."""
        print(f"Checking domain: {domain}")
        
        # Check domain registration expiry
        domain_result = self.client.tools.execute(
            tool_name="domain_name_toolkit.check_domain_expiry",
            input={"domain": domain},
            user_id=self.config.monitoring.user_id,
        )
        
        # Check SSL certificate expiry
        ssl_result = self.client.tools.execute(
            tool_name="domain_name_toolkit.check_ssl_expiry", 
            input={"domain": domain},
            user_id=self.config.monitoring.user_id,
        )
        
        return {
            "domain": domain,
            "domain_check": domain_result.output.value,
            "ssl_check": ssl_result.output.value,
            "checked_at": datetime.now().isoformat()
        }
    
    def check_all_domains(self) -> List[Dict]:
        """Check all configured domains."""
        self.results = []
        
        for domain in self.domains:
            try:
                result = self.check_domain(domain)
                self.results.append(result)
            except Exception as e:
                print(f"Error checking {domain}: {e}")
                self.results.append({
                    "domain": domain,
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                })
        
        return self.results
    
    def get_alerts(self) -> List[Dict]:
        """Get domains that need alerts (expiring within threshold)."""
        alerts = []
        
        for result in self.results:
            if "error" in result:
                continue
                
            domain_name = result["domain"]
            domain_check = result["domain_check"]
            ssl_check = result["ssl_check"]
            
            # Get threshold for this domain (per-domain override or global)
            domain_config = next((d for d in self.config.domains if d.name == domain_name), None)
            threshold = (domain_config.alert_threshold_days 
                        if domain_config and domain_config.alert_threshold_days 
                        else self.config.monitoring.alert_threshold_days)
            
            # Check domain registration
            if (domain_check.get("status") == "success" and 
                domain_check.get("days_until_expiry", 999) <= threshold):
                alerts.append({
                    "domain": domain_name,
                    "type": "domain_registration",
                    "days_until_expiry": domain_check.get("days_until_expiry"),
                    "expiration_date": domain_check.get("expiration_date"),
                    "registrar": domain_check.get("registrar"),
                    "threshold": threshold
                })
            
            # Check SSL certificate 
            if (ssl_check.get("status") == "success" and 
                ssl_check.get("days_until_expiry", 999) <= threshold):
                alerts.append({
                    "domain": domain_name,
                    "type": "ssl_certificate", 
                    "days_until_expiry": ssl_check.get("days_until_expiry"),
                    "expiration_date": ssl_check.get("expiration_date"),
                    "threshold": threshold
                })
        
        return alerts
    
    def send_email_alert(self, alerts: List[Dict]):
        """Send email alerts for expiring domains."""
        if not alerts or not self.config.notifications.email.enabled:
            return
            
        # Build email content
        subject = self.config.notifications.email.subject_template.format(count=len(alerts))
        
        body_lines = [
            "Domain Expiration Alert",
            "=" * 50,
            "",
            f"The following domains are expiring within their alert thresholds:",
            ""
        ]
        
        for alert in alerts:
            domain = alert["domain"]
            alert_type = alert["type"].replace("_", " ").title()
            days = alert["days_until_expiry"]
            exp_date = alert["expiration_date"]
            
            body_lines.append(f"🔴 {domain}")
            body_lines.append(f"   Type: {alert_type}")
            body_lines.append(f"   Days until expiry: {days}")
            body_lines.append(f"   Expiration date: {exp_date}")
            
            if alert["type"] == "domain_registration":
                body_lines.append(f"   Registrar: {alert.get('registrar', 'Unknown')}")
            
            body_lines.append("")
        
        body_lines.extend([
            "Please take action to renew these domains/certificates.",
            "",
            "This is an automated alert from Domain Monitor."
        ])
        
        body = "\n".join(body_lines)
        
        # Send to all recipients
        for recipient in self.config.notifications.email.recipients:
            try:
                self.client.tools.execute(
                    tool_name="Gmail.SendEmail",
                    input={
                        "to": recipient.email,
                        "subject": subject,
                        "body": body
                    },
                    user_id=self.config.monitoring.user_id,
                )
                print(f"📧 Alert email sent to {recipient.email}")
            except Exception as e:
                print(f"❌ Failed to send email to {recipient.email}: {e}")
    
    def send_slack_alert(self, alerts: List[Dict]):
        """Send Slack alerts for expiring domains."""
        if not alerts or not self.config.notifications.slack.enabled:
            return
            
        # Build Slack message
        message_lines = [
            self.config.notifications.slack.message_template.format(count=len(alerts)) + ":"
        ]
        
        for alert in alerts:
            domain = alert["domain"]
            alert_type = alert["type"].replace("_", " ").title()
            days = alert["days_until_expiry"]
            
            # Get emoji based on urgency
            if days <= 7:
                emoji = self.config.notifications.slack.urgency_emojis.get("critical", "🔴")
            elif days <= 30:
                emoji = self.config.notifications.slack.urgency_emojis.get("warning", "🟡")
            else:
                emoji = self.config.notifications.slack.urgency_emojis.get("info", "ℹ️")
            message_lines.append(f"{emoji} *{domain}* ({alert_type}) - {days} days left")
        
        message = "\n".join(message_lines)
        
        try:
            self.client.tools.execute(
                tool_name="Slack.SendMessage",
                input={
                    "channel": self.config.notifications.slack.channel,
                    "text": message
                },
                user_id=self.config.monitoring.user_id,
            )
            print(f"💬 Alert sent to Slack channel {self.config.notifications.slack.channel}")
        except Exception as e:
            print(f"❌ Failed to send Slack alert: {e}")
    
    def save_results(self, filename: str = None):
        """Save check results to a JSON file."""
        if not self.config.monitoring.save_results:
            return
            
        if filename is None:
            filename = self.config.monitoring.results_filename
            
        indent = 2 if self.config.advanced.json_pretty_print else None
        with open(filename, 'w') as f:
            json.dump({
                "checked_at": datetime.now().isoformat(),
                "config_summary": {
                    "domains_monitored": len(self.domains),
                    "alert_threshold_days": self.config.monitoring.alert_threshold_days,
                    "email_enabled": self.config.notifications.email.enabled,
                    "slack_enabled": self.config.notifications.slack.enabled
                },
                "results": self.results
            }, f, indent=indent)
        print(f"💾 Results saved to {filename}")
    
    def run(self):
        """Run the domain monitoring process."""
        print("🔍 Domain Monitor Starting...")
        print(f"Monitoring {len(self.domains)} domains")
        
        # Authorize tools
        self.authorize_tools()
        
        # Check all domains
        print("\n📋 Checking domains...")
        self.check_all_domains()
        
        # Get alerts
        alerts = self.get_alerts()
        
        # Save results
        self.save_results()
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Domains checked: {len(self.results)}")
        print(f"   Alerts generated: {len(alerts)}")
        
        if alerts:
            print("\n⚠️  Expiring domains/certificates:")
            for alert in alerts:
                print(f"   - {alert['domain']} ({alert['type']}) - {alert['days_until_expiry']} days")
            
            # Send notifications
            print("\n📤 Sending notifications...")
            if self.config.notifications.email.enabled:
                self.send_email_alert(alerts)
            if self.config.notifications.slack.enabled:
                self.send_slack_alert(alerts)
        else:
            print("\n✅ All domains and certificates are healthy!")
        
        print("\n🏁 Domain monitoring complete!")


def main(config_file: str = None):
    """Main entry point."""
    if not os.getenv('ARCADE_API_KEY'):
        print("❌ ARCADE_API_KEY environment variable not set")
        return 1
    
    monitor = DomainMonitor(config_file)
    monitor.run()
    return 0


if __name__ == "__main__":
    exit(main())