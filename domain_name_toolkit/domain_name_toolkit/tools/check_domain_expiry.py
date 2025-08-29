from typing import Annotated
from datetime import datetime, timezone
import whois
from arcade_tdk import tool


@tool
def check_domain_expiry(
    domain: Annotated[str, "The domain name to check (e.g., 'example.com')"],
) -> dict:
    """Check when a domain name expires using WHOIS data."""

    try:
        # Clean the domain name (remove protocol, www, etc.)
        clean_domain = (
            domain.replace("http://", "")
            .replace("https://", "")
            .replace("www.", "")
            .split("/")[0]
        )

        # Get WHOIS information
        domain_info = whois.whois(clean_domain)

        if domain_info is None:
            return {
                "domain": clean_domain,
                "status": "error",
                "message": "Domain not found.",
            }

        # Extract expiration date
        expiration_date = domain_info.expiration_date

        # Handle case where expiration_date might be a list
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        if expiration_date is None:
            return {
                "domain": clean_domain,
                "status": "error",
                "message": "Could not determine expiration date",
            }

        # Ensure expiration_date is timezone-aware
        if expiration_date.tzinfo is None:
            expiration_date = expiration_date.replace(tzinfo=timezone.utc)

        # Calculate days until expiration
        now = datetime.now(timezone.utc)
        days_until_expiry = (expiration_date - now).days

        return {
            "domain": clean_domain,
            "status": "success",
            "expiration_date": expiration_date.isoformat(),
            "days_until_expiry": days_until_expiry,
            "is_expired": days_until_expiry < 0,
            "expires_soon": 0
            <= days_until_expiry
            <= 30,  # Within 30 days but not expired
            "registrar": getattr(domain_info, "registrar", "Unknown"),
        }

    except Exception as e:
        return {
            "domain": domain,
            "status": "error",
            "message": f"Error checking domain: {str(e)}",
        }
