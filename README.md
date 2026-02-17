# MS365SITT

MS365 Security and Compliance Checking and Settings Tool

A Python-based tool for checking security and compliance settings in Microsoft 365 environments. This tool uses the Microsoft Graph API to assess various security controls and compliance configurations.

## Features

### Security Checks
- **MFA Enforcement**: Verifies Multi-Factor Authentication policies are configured
- **Conditional Access**: Checks Conditional Access policy configuration
- **Password Policies**: Reviews password policy settings
- **Guest User Management**: Identifies and reports on guest user accounts

### Compliance Checks
- **Audit Logging**: Verifies audit log accessibility and configuration
- **Data Retention**: Checks retention label and policy configuration
- **DLP Policies**: Information about Data Loss Prevention settings
- **License Compliance**: Monitors license usage and availability

## Installation

### Prerequisites
- Python 3.8 or higher
- Azure AD application with appropriate permissions (see below)

### Install from source

```bash
# Clone the repository
git clone https://github.com/SCHUONDEV/MS365SITT.git
cd MS365SITT

# Install dependencies
pip install -r requirements.txt

# Or install the package
pip install -e .
```

## Azure AD Application Setup

To use this tool, you need to register an application in Azure AD with the following permissions:

### Required Microsoft Graph API Permissions (Application):
- `Organization.Read.All` - Read organization information
- `User.Read.All` - Read user profiles
- `Policy.Read.All` - Read Conditional Access policies
- `AuditLog.Read.All` - Read audit logs
- `Directory.Read.All` - Read directory data

### Steps to set up:
1. Go to Azure Portal > Azure Active Directory > App registrations
2. Create a new registration
3. Under "API permissions", add the permissions listed above
4. Grant admin consent for your organization
5. Create a client secret under "Certificates & secrets"
6. Note down:
   - Application (client) ID
   - Directory (tenant) ID
   - Client secret value

## Configuration

Create a `.env` file in the project root with your Azure AD credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_TENANT_ID=your-tenant-id-here
```

## Usage

### Command Line Interface

Run all checks:
```bash
ms365sitt
```

Run only security checks:
```bash
ms365sitt --check-type security
```

Run only compliance checks:
```bash
ms365sitt --check-type compliance
```

### Output Formats

Console output (default):
```bash
ms365sitt --output-format console
```

JSON output:
```bash
ms365sitt --output-format json --output-file report.json
```

CSV output:
```bash
ms365sitt --output-format csv --output-file report.csv
```

Verbose mode:
```bash
ms365sitt --verbose
```

### Using as a Python module

```python
from ms365sitt.auth import GraphAuthenticator
from ms365sitt.client import GraphClient
from ms365sitt.checkers.security import MFAChecker
from ms365sitt.reporter import Reporter

# Authenticate
auth = GraphAuthenticator.from_env()
client = GraphClient(auth)

# Run a specific check
checker = MFAChecker(client)
results = checker.check()

# Generate report
reporter = Reporter(results)
print(reporter.to_console())
```

## Check Results

Each check returns results with the following statuses:
- **PASS**: Check passed, configuration meets recommended standards
- **FAIL**: Check failed, action required
- **WARNING**: Potential issue detected, review recommended
- **INFO**: Informational result, no action required
- **ERROR**: Check could not be completed due to an error

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
black ms365sitt/
```

### Linting

```bash
flake8 ms365sitt/
```

## Security Considerations

- Never commit your `.env` file or credentials to version control
- Use Azure Key Vault or similar for production deployments
- Review and limit API permissions to only what's necessary
- Regularly rotate client secrets
- Use managed identities when running in Azure

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is provided as-is for informational and compliance checking purposes. Always verify results and consult with your security team before making configuration changes to production environments.
