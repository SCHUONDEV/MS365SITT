"""Command-line interface for MS365SITT"""

import argparse
import sys
import os
from dotenv import load_dotenv

from .auth import GraphAuthenticator
from .client import GraphClient
from .checkers.security import (
    MFAChecker,
    PasswordPolicyChecker,
    ConditionalAccessChecker,
    GuestUserChecker,
)
from .checkers.compliance import (
    AuditLogChecker,
    DataRetentionChecker,
    DLPPolicyChecker,
    LicenseComplianceChecker,
)
from .reporter import Reporter


def run_security_checks(client: GraphClient) -> list:
    """Run all security checks"""
    results = []

    print("Running security checks...")

    checkers = [
        MFAChecker(client),
        PasswordPolicyChecker(client),
        ConditionalAccessChecker(client),
        GuestUserChecker(client),
    ]

    for checker in checkers:
        print(f"  - Running {checker.__class__.__name__}...")
        try:
            results.extend(checker.check())
        except Exception as e:
            print(f"    Error: {str(e)}")

    return results


def run_compliance_checks(client: GraphClient) -> list:
    """Run all compliance checks"""
    results = []

    print("Running compliance checks...")

    checkers = [
        AuditLogChecker(client),
        DataRetentionChecker(client),
        DLPPolicyChecker(client),
        LicenseComplianceChecker(client),
    ]

    for checker in checkers:
        print(f"  - Running {checker.__class__.__name__}...")
        try:
            results.extend(checker.check())
        except Exception as e:
            print(f"    Error: {str(e)}")

    return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MS365 Security and Compliance Checking and Settings Tool"
    )

    parser.add_argument(
        "--check-type",
        choices=["all", "security", "compliance"],
        default="all",
        help="Type of checks to run (default: all)",
    )

    parser.add_argument(
        "--output-format",
        choices=["console", "json", "csv"],
        default="console",
        help="Output format (default: console)",
    )

    parser.add_argument(
        "--output-file", type=str, help="Output file path for JSON or CSV format"
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed information"
    )

    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
    )

    args = parser.parse_args()

    # Load environment variables
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
    else:
        load_dotenv()

    try:
        # Authenticate
        print("Authenticating to Microsoft Graph API...")
        authenticator = GraphAuthenticator.from_env()
        client = GraphClient(authenticator)

        # Run checks
        all_results = []

        if args.check_type in ["all", "security"]:
            all_results.extend(run_security_checks(client))

        if args.check_type in ["all", "compliance"]:
            all_results.extend(run_compliance_checks(client))

        # Generate report
        print("\n" + "=" * 80)
        reporter = Reporter(all_results)

        if args.output_format == "console":
            print("\n" + reporter.to_console(verbose=args.verbose))
            print("\n" + reporter.get_summary_text())

        elif args.output_format == "json":
            if args.output_file:
                reporter.to_json(args.output_file)
                print(f"\nReport saved to {args.output_file}")
            else:
                print("\n" + reporter.to_json())

        elif args.output_format == "csv":
            if not args.output_file:
                print("Error: --output-file required for CSV format")
                sys.exit(1)
            reporter.to_csv(args.output_file)
            print(f"\nReport saved to {args.output_file}")

        print("\nDone!")

    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        print("\nPlease ensure the following environment variables are set:")
        print("  - AZURE_CLIENT_ID")
        print("  - AZURE_CLIENT_SECRET")
        print("  - AZURE_TENANT_ID")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
