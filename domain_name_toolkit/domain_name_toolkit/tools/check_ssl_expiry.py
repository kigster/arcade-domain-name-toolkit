from typing import Annotated
import ssl
import socket
from datetime import datetime, timezone
import whois
from arcade_tdk import tool

@tool
def check_ssl_expiry(
    domain: Annotated[str, "The domain name to check SSL certificate (e.g., 'example.com')"],
    port: Annotated[int, "The port to check SSL certificate (e.g., 443)"] = 443
) -> dict:
    """Check when a domain's SSL certificate expires."""
    
    try:
        # Clean the domain name
        clean_domain = domain.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
        
        # Get SSL certificate information
        context = ssl.create_default_context()
        
        with socket.create_connection((clean_domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=clean_domain) as ssock:
                cert = ssock.getpeercert()
        
        # Extract expiration date
        expiry_date_str = cert['notAfter']
        # Parse the certificate date format: 'MMM DD HH:MM:SS YYYY GMT'
        expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        
        # Calculate days until expiration
        now = datetime.now(timezone.utc)
        days_until_expiry = (expiry_date - now).days
        
        return {
            "domain": clean_domain,
            "status": "success",
            "expiration_date": expiry_date.isoformat(),
            "days_until_expiry": days_until_expiry,
            "is_expired": days_until_expiry < 0,
            "expires_soon": 0 <= days_until_expiry <= 30,  # Within 30 days but not expired
            "subject": cert.get('subject', []),
            "issuer": cert.get('issuer', [])
        }
        
    except socket.gaierror:
        return {
            "domain": domain,
            "status": "error",
            "message": "Domain not found or not reachable"
        }
    except socket.timeout:
        return {
            "domain": domain,
            "status": "error", 
            "message": "Connection timeout"
        }
    except ssl.SSLError as e:
        return {
            "domain": domain,
            "status": "error",
            "message": f"SSL error: {str(e)}"
        }
    except Exception as e:
        return {
            "domain": domain,
            "status": "error",
            "message": f"Error checking SSL certificate: {str(e)}"
        }