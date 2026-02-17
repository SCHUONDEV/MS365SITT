"""Compliance-related checkers"""

from typing import Dict, List, Any
from . import BaseChecker


class AuditLogChecker(BaseChecker):
    """Check audit log configuration"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check if audit logging is enabled
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Try to access audit logs to verify they're enabled
            # This endpoint requires appropriate permissions
            audit_logs = self.client.get(
                "/auditLogs/directoryAudits?$top=1", use_beta=True
            )

            if "value" in audit_logs:
                self.add_result(
                    check_name="Audit Log Access",
                    status="PASS",
                    message="Audit logs are accessible and enabled",
                    details={},
                )
            else:
                self.add_result(
                    check_name="Audit Log Access",
                    status="WARNING",
                    message="Unable to verify audit log status",
                    details={},
                )

        except Exception as e:
            # If we get a permissions error, logs might be enabled but we can't access them
            if "Insufficient privileges" in str(e) or "403" in str(e):
                self.add_result(
                    check_name="Audit Log Access",
                    status="WARNING",
                    message="Insufficient permissions to verify audit logs",
                    details={"error": str(e)},
                )
            else:
                self.add_result(
                    check_name="Audit Log Access",
                    status="ERROR",
                    message=f"Failed to check audit logs: {str(e)}",
                    details={"error": str(e)},
                )

        return self.results


class DataRetentionChecker(BaseChecker):
    """Check data retention policies"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check retention policy configuration
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Check for retention labels
            retention_labels = self.client.get_all_pages(
                "/security/labels/retentionLabels", use_beta=True
            )

            if len(retention_labels) > 0:
                self.add_result(
                    check_name="Retention Labels",
                    status="PASS",
                    message=f"Found {len(retention_labels)} retention label(s) configured",
                    details={"label_count": len(retention_labels)},
                )
            else:
                self.add_result(
                    check_name="Retention Labels",
                    status="WARNING",
                    message="No retention labels found",
                    details={"label_count": 0},
                )

        except Exception as e:
            self.add_result(
                check_name="Retention Policies",
                status="ERROR",
                message=f"Failed to check retention policies: {str(e)}",
                details={"error": str(e)},
            )

        return self.results


class DLPPolicyChecker(BaseChecker):
    """Check Data Loss Prevention policies"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check DLP policy configuration
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Note: DLP policies are typically managed through Security & Compliance Center
            # This is a simplified check
            self.add_result(
                check_name="DLP Policies",
                status="INFO",
                message="DLP policy check requires Security & Compliance Center API access",
                details={
                    "note": "Configure DLP policies through Microsoft Purview compliance portal"
                },
            )

        except Exception as e:
            self.add_result(
                check_name="DLP Policies",
                status="ERROR",
                message=f"Failed to check DLP policies: {str(e)}",
                details={"error": str(e)},
            )

        return self.results


class LicenseComplianceChecker(BaseChecker):
    """Check license compliance"""

    def check(self) -> List[Dict[str, Any]]:
        """
        Check license assignment and compliance
        
        Returns:
            List of check results
        """
        self.results = []

        try:
            # Get subscribed SKUs
            skus = self.client.get_all_pages("/subscribedSkus")

            total_licenses = 0
            consumed_licenses = 0

            for sku in skus:
                if sku.get("capabilityStatus") == "Enabled":
                    enabled = sku.get("prepaidUnits", {}).get("enabled", 0)
                    consumed = sku.get("consumedUnits", 0)
                    total_licenses += enabled
                    consumed_licenses += consumed

            if total_licenses > 0:
                usage_percent = (consumed_licenses / total_licenses) * 100
                self.add_result(
                    check_name="License Usage",
                    status="INFO",
                    message=f"Using {consumed_licenses} of {total_licenses} licenses ({usage_percent:.1f}%)",
                    details={
                        "total": total_licenses,
                        "consumed": consumed_licenses,
                        "available": total_licenses - consumed_licenses,
                        "usage_percent": round(usage_percent, 2),
                    },
                )

                if usage_percent > 90:
                    self.add_result(
                        check_name="License Availability",
                        status="WARNING",
                        message=f"License usage is high ({usage_percent:.1f}%)",
                        details={},
                    )

        except Exception as e:
            self.add_result(
                check_name="License Compliance",
                status="ERROR",
                message=f"Failed to check licenses: {str(e)}",
                details={"error": str(e)},
            )

        return self.results
