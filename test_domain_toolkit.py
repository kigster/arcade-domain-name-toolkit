#!/usr/bin/env python3

"""
Test script for the Domain Name Toolkit
"""

from domain_name_toolkit.tools.check_domain_expiry import check_domain_expiry
from domain_name_toolkit.tools.check_ssl_expiry import check_ssl_expiry


def test_domain_functions():
    """Test the domain checking functions directly."""

    test_domains = ["google.com", "github.com", "example.com"]

    print("🔍 Testing Domain Name Toolkit Functions")
    print("=" * 50)

    for domain in test_domains:
        print(f"\n📋 Testing domain: {domain}")
        print("-" * 30)

        # Test domain expiry check
        print("🌐 Checking domain expiry...")
        try:
            domain_result = check_domain_expiry(domain)
            print(f"   Status: {domain_result.get('status', 'unknown')}")
            if domain_result.get("status") == "success":
                print(f"   Expires: {domain_result.get('expiration_date', 'unknown')}")
                print(
                    f"   Days left: {domain_result.get('days_until_expiry', 'unknown')}"
                )
                print(f"   Expires soon: {domain_result.get('expires_soon', False)}")
                print(f"   Registrar: {domain_result.get('registrar', 'unknown')}")
            else:
                print(f"   Error: {domain_result.get('message', 'unknown error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test SSL expiry check
        print("🔒 Checking SSL expiry...")
        try:
            ssl_result = check_ssl_expiry(domain)
            print(f"   Status: {ssl_result.get('status', 'unknown')}")
            if ssl_result.get("status") == "success":
                print(f"   Expires: {ssl_result.get('expiration_date', 'unknown')}")
                print(f"   Days left: {ssl_result.get('days_until_expiry', 'unknown')}")
                print(f"   Expires soon: {ssl_result.get('expires_soon', False)}")
            else:
                print(f"   Error: {ssl_result.get('message', 'unknown error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_domain_functions()
