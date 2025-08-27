# Domain Monitor Toolkit

A complete domain and SSL certificate monitoring solution built with Arcade.dev that automatically checks domain expiration dates and SSL certificate validity, sending alerts via email and Slack when they're about to expire.

## Features

- **Domain Registration Monitoring**: Checks WHOIS data for domain expiration dates
- **SSL Certificate Monitoring**: Validates SSL certificate expiration dates  
- **Email Alerts**: Sends detailed email notifications via Gmail
- **Slack Integration**: Optional Slack channel notifications
- **Configurable Thresholds**: Set custom alert timeframes (default: 30 days)
- **JSON Logging**: Saves all check results to structured JSON files
- **Error Handling**: Graceful handling of network issues and API failures

## Project Structure

```
domain_name_toolkit/                 # Custom Arcade toolkit
├── domain_name_toolkit/
│   └── tools/
│       └── hello.py                # Domain checking functions
├── pyproject.toml                  # Toolkit configuration
└── README.md

domain_monitor_app.py               # Main monitoring application
domain_config.py                   # Configuration file
test_domain_toolkit.py             # Direct function tests
DOMAIN_MONITOR_README.md           # This file
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install arcade-ai arcadepy python-whois
   ```

2. **Install the custom toolkit**:
   ```bash
   cd domain_name_toolkit
   pip install -e .
   ```

3. **Set up Arcade API key**:
   ```bash
   export ARCADE_API_KEY="your-api-key-here"
   ```

4. **Authenticate with Arcade services**:
   ```bash
   arcade login
   ```

## Configuration

Edit `domain_config.py` to customize your monitoring setup:

```python
# Domains to monitor
DOMAINS_TO_MONITOR = [
    "yourdomain.com",
    "anotherdomain.org",
    "example.net"
]

# Alert settings
ALERT_THRESHOLD_DAYS = 30  # Alert when expiring within 30 days

# Email notifications
ENABLE_EMAIL_ALERTS = True
EMAIL_RECIPIENTS = [
    "admin@yourdomain.com",
    "alerts@company.com"
]

# Slack notifications (optional)
ENABLE_SLACK_ALERTS = True
SLACK_CHANNEL = "#alerts"
```

## Usage

### Run the Complete Monitoring System

```bash
python domain_monitor_app.py
```

This will:
1. Check all configured domains and SSL certificates
2. Generate alerts for expiring items
3. Send email and/or Slack notifications
4. Save results to JSON file

### Test Individual Functions

```bash
python test_domain_toolkit.py
```

This tests the toolkit functions directly without using Arcade's API.

### Example Output

```
🔍 Domain Monitor Starting...
Monitoring 4 domains

📋 Checking domains...
Checking domain: google.com
Checking domain: github.com
Checking domain: example.com
Checking domain: stackoverflow.com

📊 Summary:
   Domains checked: 4
   Alerts generated: 0

✅ All domains and certificates are healthy!

💾 Results saved to domain_check_results.json

🏁 Domain monitoring complete!
```

## Toolkit Functions

### `check_domain_expiry(domain)`

Checks domain registration expiration using WHOIS data.

**Parameters:**
- `domain` (str): Domain name to check (e.g., 'example.com')

**Returns:**
```json
{
  "domain": "example.com",
  "status": "success",
  "expiration_date": "2026-08-13T04:00:00+00:00",
  "days_until_expiry": 350,
  "is_expired": false,
  "expires_soon": false,
  "registrar": "Example Registrar Inc."
}
```

### `check_ssl_expiry(domain)`

Checks SSL certificate expiration by connecting to the domain.

**Parameters:**
- `domain` (str): Domain name to check SSL certificate

**Returns:**
```json
{
  "domain": "example.com", 
  "status": "success",
  "expiration_date": "2026-01-15T23:59:59+00:00",
  "days_until_expiry": 141,
  "is_expired": false,
  "expires_soon": false,
  "subject": [...],
  "issuer": [...]
}
```

## Alert System

### Email Alerts

When domains or certificates are expiring within the threshold:

- **Subject**: "🚨 Domain Expiration Alert - X domain(s) expiring soon"
- **Content**: Detailed breakdown of each expiring item with:
  - Domain name and type (registration vs SSL)
  - Days until expiration
  - Expiration date
  - Additional metadata

### Slack Alerts

Concise Slack messages with:
- 🔴 Critical alerts (≤7 days)
- 🟡 Warning alerts (8-30 days)
- Domain name and expiration timeline

## Automation

### Cron Job Setup

Add to your crontab for daily monitoring:

```bash
# Run domain check every day at 9 AM
0 9 * * * cd /path/to/project && python domain_monitor_app.py
```

### GitHub Actions

Create `.github/workflows/domain-check.yml`:

```yaml
name: Domain Monitor
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  
jobs:
  check-domains:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd domain_name_toolkit && pip install -e .
      - name: Run domain check
        env:
          ARCADE_API_KEY: ${{ secrets.ARCADE_API_KEY }}
        run: python domain_monitor_app.py
```

## Troubleshooting

### Common Issues

1. **"Not logged in to Arcade CLI"**
   ```bash
   arcade login
   # Follow the authentication prompts
   ```

2. **WHOIS lookup failures**
   - Some domains may have restricted WHOIS access
   - Check domain spelling and availability
   - Verify internet connectivity

3. **SSL connection errors**
   - Domain may not support HTTPS
   - Firewall blocking port 443
   - Certificate may already be expired

4. **Toolkit not found**
   ```bash
   cd domain_name_toolkit
   pip install -e .
   ```

### Error Handling

The toolkit includes comprehensive error handling:
- Network timeouts and connection failures
- WHOIS service unavailability  
- SSL handshake errors
- Invalid domain names
- API rate limiting

All errors are logged with descriptive messages and don't stop the monitoring process.

## Development

### Adding New Domains

Simply add domains to the `DOMAINS_TO_MONITOR` list in `domain_config.py`.

### Customizing Alerts

Modify alert thresholds, email templates, or Slack message formats in `domain_monitor_app.py`.

### Extending Functionality

The toolkit can be extended with additional functions:
- DNS record monitoring
- Website uptime checks
- Certificate chain validation
- Multi-domain SSL certificate support

## Dependencies

- **arcade-ai**: Arcade.dev AI toolkit framework
- **arcadepy**: Arcade Python client
- **python-whois**: WHOIS lookup functionality
- **ssl**: Built-in SSL certificate checking
- **socket**: Network connection handling

## License

This project is part of the Arcade.dev sample toolkit and follows the same licensing terms.

## Support

For issues with the toolkit:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure Arcade API key is properly configured
4. Test individual functions with `test_domain_toolkit.py`

For Arcade.dev platform issues, visit: https://docs.arcade.dev