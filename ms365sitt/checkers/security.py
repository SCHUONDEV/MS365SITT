"""Security-related compliance checkers"""

from typing import Dict, List, Any, Optional
from . import BaseChecker


class MFAChecker(BaseChecker):
    """Check Multi-Factor Authentication enforcement"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check MFA enforcement status
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Get conditional access policies
            policies = self.client.get_all_pages(
                "/identity/conditionalAccess/policies", use_beta=True
            )

            mfa_policies = [
                p
                for p in policies
                if p.get("state") == "enabled"
                and any(
                    "mfa" in grant.lower()
                    for grant in p.get("grantControls", {}).get("builtInControls", [])
                )
            ]

            if mfa_policies:
                self.add_result(
                    check_name="MFA Enforcement",
                    status="PASS",
                    message=f"Found {len(mfa_policies)} active MFA policy/policies",
                    details={"policy_count": len(mfa_policies)},
                )
            else:
                self.add_result(
                    check_name="MFA Enforcement",
                    status="FAIL",
                    message="No active MFA enforcement policies found",
                    details={"policy_count": 0},
                )

        except Exception as e:
            self.add_result(
                check_name="MFA Enforcement",
                status="ERROR",
                message=f"Failed to check MFA policies: {str(e)}",
                details={"error": str(e)},
            )

        return self.results


class PasswordPolicyChecker(BaseChecker):
    """Check password policy settings"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check password policy configuration
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Get domain password policies
            domains = self.client.get_all_pages("/domains")

            for domain in domains:
                if domain.get("isDefault"):
                    # Check password policy via organization settings
                    settings = self.client.get("/organization")

                    if "value" in settings and len(settings["value"]) > 0:
                        org = settings["value"][0]

                        # Check password validity period
                        password_validity = org.get("passwordValidityPeriodInDays")
                        if password_validity and password_validity <= 90:
                            self.add_result(
                                check_name="Password Expiry Policy",
                                status="PASS",
                                message=f"Password expiry set to {password_validity} days",
                                details={"validity_days": password_validity},
                            )
                        else:
                            self.add_result(
                                check_name="Password Expiry Policy",
                                status="WARNING",
                                message=f"Password expiry is {password_validity} days (recommended: 90 or less)",
                                details={"validity_days": password_validity},
                            )

        except Exception as e:
            self.add_result(
                check_name="Password Policy",
                status="ERROR",
                message=f"Failed to check password policies: {str(e)}",
                details={"error": str(e)},
            )

        return self.results


class ConditionalAccessChecker(BaseChecker):
    """Check Conditional Access policies"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check Conditional Access policy configuration
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            policies = self.client.get_all_pages(
                "/identity/conditionalAccess/policies", use_beta=True
            )

            enabled_policies = [p for p in policies if p.get("state") == "enabled"]
            disabled_policies = [p for p in policies if p.get("state") != "enabled"]

            self.add_result(
                check_name="Conditional Access Policies",
                status="INFO",
                message=f"Found {len(enabled_policies)} enabled and {len(disabled_policies)} disabled policies",
                details={
                    "enabled_count": len(enabled_policies),
                    "disabled_count": len(disabled_policies),
                    "total_count": len(policies),
                },
            )

            if len(enabled_policies) == 0:
                self.add_result(
                    check_name="Conditional Access Configuration",
                    status="FAIL",
                    message="No enabled Conditional Access policies found",
                    details={},
                )
            else:
                self.add_result(
                    check_name="Conditional Access Configuration",
                    status="PASS",
                    message="Conditional Access policies are configured",
                    details={},
                )

        except Exception as e:
            self.add_result(
                check_name="Conditional Access",
                status="ERROR",
                message=f"Failed to check Conditional Access: {str(e)}",
                details={"error": str(e)},
            )

        return self.results


class GuestUserChecker(BaseChecker):
    """Check guest user settings and risks"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check guest user configuration
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Get all users and filter for guests
            users = self.client.get_all_pages("/users?$select=userType,userPrincipalName")

            guest_users = [u for u in users if u.get("userType") == "Guest"]

            if len(guest_users) > 0:
                self.add_result(
                    check_name="Guest Users",
                    status="INFO",
                    message=f"Found {len(guest_users)} guest user(s) in the tenant",
                    details={"guest_count": len(guest_users)},
                )
            else:
                self.add_result(
                    check_name="Guest Users",
                    status="INFO",
                    message="No guest users found in the tenant",
                    details={"guest_count": 0},
                )

        except Exception as e:
            self.add_result(
                check_name="Guest Users",
                status="ERROR",
                message=f"Failed to check guest users: {str(e)}",
                details={"error": str(e)},
            )

        return self.results
