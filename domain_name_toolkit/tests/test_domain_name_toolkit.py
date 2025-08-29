from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import socket

from domain_name_toolkit.tools.check_domain_expiry import check_domain_expiry
from domain_name_toolkit.tools.check_ssl_expiry import check_ssl_expiry


class TestCheckDomainExpiry:
    """Tests for check_domain_expiry function"""

    @patch("whois.whois")
    def test_successful_domain_check(self, mock_whois):
        """Test successful domain expiration check"""
        # Mock WHOIS response
        mock_whois_obj = Mock()
        future_date = datetime.now(timezone.utc) + timedelta(days=100)
        mock_whois_obj.expiration_date = future_date
        mock_whois_obj.registrar = "Test Registrar"
        mock_whois.return_value = mock_whois_obj

        result = check_domain_expiry("test-domain.com")

        assert result["domain"] == "test-domain.com"
        assert result["status"] == "success"
        assert "expiration_date" in result
        assert "days_until_expiry" in result
        assert result["is_expired"] is False
        assert result["expires_soon"] is False
        assert result["registrar"] == "Test Registrar"
        mock_whois.assert_called_once_with("test-domain.com")

    @patch("whois.whois")
    def test_domain_check_expired(self, mock_whois):
        """Test domain check for expired domain"""
        mock_whois_obj = Mock()
        expired_date = datetime.now(timezone.utc) - timedelta(days=10)
        mock_whois_obj.expiration_date = expired_date
        mock_whois_obj.registrar = "Test Registrar"
        mock_whois.return_value = mock_whois_obj

        result = check_domain_expiry("expired-domain.com")

        assert result["status"] == "success"
        assert result["is_expired"] is True
        assert result["expires_soon"] is False
        assert result["days_until_expiry"] < 0

    @patch("whois.whois")
    def test_domain_check_expiring_soon(self, mock_whois):
        """Test domain check for domain expiring soon"""
        mock_whois_obj = Mock()
        soon_date = datetime.now(timezone.utc) + timedelta(days=15)
        mock_whois_obj.expiration_date = soon_date
        mock_whois_obj.registrar = "Test Registrar"
        mock_whois.return_value = mock_whois_obj

        result = check_domain_expiry("expiring-domain.com")

        assert result["status"] == "success"
        assert result["expires_soon"] is True
        assert result["is_expired"] is False
        assert 0 < result["days_until_expiry"] <= 30

    @patch("whois.whois")
    def test_domain_check_no_expiration_date(self, mock_whois):
        """Test domain check when no expiration date is found"""
        mock_whois_obj = Mock()
        mock_whois_obj.expiration_date = None
        mock_whois.return_value = mock_whois_obj

        result = check_domain_expiry("test-domain.com")

        assert result["status"] == "error"
        assert result["message"] == "Could not determine expiration date"

    @patch("whois.whois")
    def test_domain_check_exception(self, mock_whois):
        """Test domain check when WHOIS throws exception"""
        mock_whois.side_effect = Exception("WHOIS lookup failed")

        result = check_domain_expiry("error-domain.com")

        assert result["status"] == "error"
        assert "Error checking domain" in result["message"]

    def test_domain_name_cleaning(self):
        """Test that domain names are properly cleaned"""
        with patch("whois.whois") as mock_whois:
            mock_whois_obj = Mock()
            future_date = datetime.now(timezone.utc) + timedelta(days=100)
            mock_whois_obj.expiration_date = future_date
            mock_whois_obj.registrar = "Test Registrar"
            mock_whois.return_value = mock_whois_obj

            # Test various domain formats
            test_cases = [
                "https://example.com",
                "http://www.example.com",
                "www.example.com",
                "example.com/path",
                "example.com",
            ]

            for test_domain in test_cases:
                result = check_domain_expiry(test_domain)
                assert result["domain"] == "example.com"
                mock_whois.assert_called_with("example.com")


class TestCheckSSLExpiry:
    """Tests for check_ssl_expiry function"""

    @patch("ssl.create_default_context")
    @patch("socket.create_connection")
    def test_successful_ssl_check(self, mock_create_connection, mock_ssl_context):
        """Test successful SSL certificate check"""
        # Mock SSL certificate
        future_date = datetime.now(timezone.utc) + timedelta(days=50)
        mock_cert = {
            "notAfter": future_date.strftime("%b %d %H:%M:%S %Y %Z"),
            "subject": [[["commonName", "test-domain.com"]]],
            "issuer": [[["commonName", "Test CA"]]],
        }

        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssl_socket
        mock_ssl_context.return_value = mock_context

        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket

        result = check_ssl_expiry("test-domain.com")

        assert result["domain"] == "test-domain.com"
        assert result["status"] == "success"
        assert "expiration_date" in result
        assert "days_until_expiry" in result
        assert result["is_expired"] is False
        assert result["expires_soon"] is False
        assert "subject" in result
        assert "issuer" in result

        # Verify connection was made to port 443
        mock_create_connection.assert_called_once_with(
            ("test-domain.com", 443), timeout=10
        )

    @patch("ssl.create_default_context")
    @patch("socket.create_connection")
    def test_ssl_check_expiring_soon(self, mock_create_connection, mock_ssl_context):
        """Test SSL check for certificate expiring soon"""
        # Certificate expiring in 10 days
        soon_date = datetime.now(timezone.utc) + timedelta(days=10)
        mock_cert = {
            "notAfter": soon_date.strftime("%b %d %H:%M:%S %Y %Z"),
            "subject": [[["commonName", "test-domain.com"]]],
            "issuer": [[["commonName", "Test CA"]]],
        }

        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssl_socket
        mock_ssl_context.return_value = mock_context

        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket

        result = check_ssl_expiry("expiring-ssl.com")

        assert result["status"] == "success"
        assert result["expires_soon"] is True
        assert result["is_expired"] is False
        assert 0 < result["days_until_expiry"] <= 30

    @patch("ssl.create_default_context")
    @patch("socket.create_connection")
    def test_ssl_check_expired_cert(self, mock_create_connection, mock_ssl_context):
        """Test SSL check for expired certificate"""
        # Certificate expired 5 days ago
        past_date = datetime.now(timezone.utc) - timedelta(days=5)
        mock_cert = {
            "notAfter": past_date.strftime("%b %d %H:%M:%S %Y %Z"),
            "subject": [[["commonName", "expired-ssl.com"]]],
            "issuer": [[["commonName", "Test CA"]]],
        }

        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssl_socket
        mock_ssl_context.return_value = mock_context

        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket

        result = check_ssl_expiry("expired-ssl.com")

        assert result["status"] == "success"
        assert result["is_expired"] is True
        assert result["expires_soon"] is False
        assert result["days_until_expiry"] < 0

    @patch("socket.create_connection")
    def test_ssl_check_connection_error(self, mock_create_connection):
        """Test SSL check when connection fails"""
        mock_create_connection.side_effect = socket.gaierror("Name resolution failed")

        result = check_ssl_expiry("nonexistent-domain.com")

        assert result["status"] == "error"
        assert result["message"] == "Domain not found or not reachable"

    @patch("socket.create_connection")
    def test_ssl_check_timeout(self, mock_create_connection):
        """Test SSL check when connection times out"""
        mock_create_connection.side_effect = socket.timeout("Connection timed out")

        result = check_ssl_expiry("slow-domain.com")

        assert result["status"] == "error"
        assert result["message"] == "Connection timeout"

    def test_ssl_domain_name_cleaning(self):
        """Test that SSL check properly cleans domain names"""
        with patch("ssl.create_default_context") as mock_ssl_context:
            with patch("socket.create_connection") as mock_create_connection:
                # Mock successful SSL check
                mock_ssl_socket = MagicMock()
                future_date = datetime.now(timezone.utc) + timedelta(days=50)
                mock_ssl_socket.getpeercert.return_value = {
                    "notAfter": future_date.strftime("%b %d %H:%M:%S %Y %Z"),
                    "subject": [[["commonName", "example.com"]]],
                    "issuer": [[["commonName", "Test CA"]]],
                }

                mock_context = MagicMock()
                mock_context.wrap_socket.return_value.__enter__.return_value = (
                    mock_ssl_socket
                )
                mock_ssl_context.return_value = mock_context

                mock_socket = MagicMock()
                mock_create_connection.return_value = mock_socket

                # Test various domain formats
                test_cases = [
                    "https://example.com",
                    "http://www.example.com",
                    "www.example.com",
                    "example.com/path",
                    "example.com",
                ]

                for test_domain in test_cases:
                    result = check_ssl_expiry(test_domain)
                    assert result["domain"] == "example.com"
                    # Verify connection was made to cleaned domain
                    mock_create_connection.assert_called_with(
                        ("example.com", 443), timeout=10
                    )
