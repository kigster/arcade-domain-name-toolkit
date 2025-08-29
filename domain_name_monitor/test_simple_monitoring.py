#!/usr/bin/env python3

"""
Simple test of domain monitoring without Arcade authorization
This tests the core functionality by directly calling the toolkit functions
"""

from domain_name_toolkit.tools.check_domain_expiry import check_domain_expiry
from domain_name_toolkit.tools.check_ssl_expiry import check_ssl_expiry
import json
from datetime import datetime

# Test domains
TEST_DOMAINS = ["google.com", "github.com"]

ALERT_THRESHOLD_DAYS = 30


def simple_domain_check():
    """Perform a simple domain check without Arcade orchestration."""

    print("🔍 Simple Domain Monitor Test")
    print("=" * 40)

    results = []
    alerts = []

    for domain in TEST_DOMAINS:
        print(f"\n📋 Checking {domain}...")

        # Check domain expiry
        domain_result = check_domain_expiry(domain)
        ssl_result = check_ssl_expiry(domain)

        result = {
            "domain": domain,
            "domain_check": domain_result,
            "ssl_check": ssl_result,
            "checked_at": datetime.now().isoformat(),
        }
        results.append(result)

        # Check for alerts
        if (
            domain_result.get("status") == "success"
            and domain_result.get("days_until_expiry", 999) <= ALERT_THRESHOLD_DAYS
        ):
            alerts.append(
                {
                    "domain": domain,
                    "type": "domain_registration",
                    "days": domain_result.get("days_until_expiry"),
                }
            )

        if (
            ssl_result.get("status") == "success"
            and ssl_result.get("days_until_expiry", 999) <= ALERT_THRESHOLD_DAYS
        ):
            alerts.append(
                {
                    "domain": domain,
                    "type": "ssl_certificate",
                    "days": ssl_result.get("days_until_expiry"),
                }
            )

        # Print results
        if domain_result.get("status") == "success":
            print(
                f"   🌐 Domain expires in {domain_result.get('days_until_expiry')} days"
            )
        else:
            print(f"   🌐 Domain check failed: {domain_result.get('message')}")

        if ssl_result.get("status") == "success":
            print(f"   🔒 SSL expires in {ssl_result.get('days_until_expiry')} days")
        else:
            print(f"   🔒 SSL check failed: {ssl_result.get('message')}")

    # Summary
    print("\n📊 Summary:")
    print(f"   Domains checked: {len(results)}")
    print(f"   Alerts generated: {len(alerts)}")

    if alerts:
        print("\n⚠️  Expiring items:")
        for alert in alerts:
            print(f"   - {alert['domain']} ({alert['type']}) - {alert['days']} days")
    else:
        print("\n✅ All domains and certificates are healthy!")

    # Save results
    with open("simple_test_results.json", "w") as f:
        json.dump(
            {
                "checked_at": datetime.now().isoformat(),
                "results": results,
                "alerts": alerts,
            },
            f,
            indent=2,
        )

    print("\n💾 Results saved to simple_test_results.json")


if __name__ == "__main__":
    simple_domain_check()
