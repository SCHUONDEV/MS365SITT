# Examples

This directory contains example usage of MS365SITT.

## Basic Usage Example

```python
#!/usr/bin/env python3
"""
Example script showing how to use MS365SITT programmatically
"""

from ms365sitt.auth import GraphAuthenticator
from ms365sitt.client import GraphClient
from ms365sitt.checkers.security import MFAChecker, ConditionalAccessChecker
from ms365sitt.checkers.compliance import AuditLogChecker, LicenseComplianceChecker
from ms365sitt.reporter import Reporter

def main():
    # Authenticate using environment variables
    print("Authenticating...")
    authenticator = GraphAuthenticator.from_env()
    client = GraphClient(authenticator)

    # Run security checks
    print("Running security checks...")
    mfa_checker = MFAChecker(client)
    ca_checker = ConditionalAccessChecker(client)
    
    results = []
    results.extend(mfa_checker.check())
    results.extend(ca_checker.check())

    # Run compliance checks
    print("Running compliance checks...")
    audit_checker = AuditLogChecker(client)
    license_checker = LicenseComplianceChecker(client)
    
    results.extend(audit_checker.check())
    results.extend(license_checker.check())

    # Generate and display report
    reporter = Reporter(results)
    print("\n" + "="*80)
    print(reporter.to_console(verbose=True))
    print("\n" + reporter.get_summary_text())
    
    # Save to JSON
    reporter.to_json("compliance_report.json")
    print("\nReport saved to compliance_report.json")

if __name__ == "__main__":
    main()
```

## Running Individual Checkers

```python
from ms365sitt.auth import GraphAuthenticator
from ms365sitt.client import GraphClient
from ms365sitt.checkers.security import GuestUserChecker

# Setup
auth = GraphAuthenticator.from_env()
client = GraphClient(auth)

# Run specific check
checker = GuestUserChecker(client)
results = checker.check()

# Print results
for result in results:
    print(f"{result['status']}: {result['message']}")
```

## Custom Reporting

```python
from ms365sitt.reporter import Reporter

# Assuming you have results from checkers
reporter = Reporter(results)

# Console output
print(reporter.to_console())

# JSON output
json_report = reporter.to_json()
print(json_report)

# Save to file
reporter.to_json("report.json")
reporter.to_csv("report.csv")

# Get summary
summary = reporter.get_summary_text()
print(summary)
```
