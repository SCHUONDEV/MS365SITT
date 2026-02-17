"""Reporting module for compliance check results"""

import json
import csv
from typing import List, Dict, Any
from datetime import datetime
from tabulate import tabulate


class Reporter:
    """Generate reports from compliance check results"""

    def __init__(self, results: List[Dict[str, Any]]):
        """
        Initialize reporter
        
        Args:
            results: List of check results
        """
        self.results = results
        self.timestamp = datetime.now().isoformat()

    def to_console(self, verbose: bool = False) -> str:
        """
        Generate console-friendly report
        
        Args:
            verbose: Include detailed information
            
        Returns:
            Formatted string for console output
        """
        if not self.results:
            return "No results to display"

        # Prepare data for table
        table_data = []
        for result in self.results:
            row = [
                result.get("check", "Unknown"),
                result.get("status", "Unknown"),
                result.get("message", ""),
            ]
            if verbose and result.get("details"):
                row.append(str(result.get("details")))
            table_data.append(row)

        headers = ["Check", "Status", "Message"]
        if verbose:
            headers.append("Details")

        return tabulate(table_data, headers=headers, tablefmt="grid")

    def to_json(self, filepath: str = None) -> str:
        """
        Generate JSON report
        
        Args:
            filepath: Optional file path to save JSON
            
        Returns:
            JSON string
        """
        report = {
            "timestamp": self.timestamp,
            "total_checks": len(self.results),
            "summary": self._get_summary(),
            "results": self.results,
        }

        json_str = json.dumps(report, indent=2)

        if filepath:
            with open(filepath, "w") as f:
                f.write(json_str)

        return json_str

    def to_csv(self, filepath: str) -> None:
        """
        Generate CSV report
        
        Args:
            filepath: File path to save CSV
        """
        if not self.results:
            return

        with open(filepath, "w", newline="") as f:
            fieldnames = ["check", "status", "message", "details"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                writer.writerow(
                    {
                        "check": result.get("check", ""),
                        "status": result.get("status", ""),
                        "message": result.get("message", ""),
                        "details": json.dumps(result.get("details", {})),
                    }
                )

    def _get_summary(self) -> Dict[str, int]:
        """
        Get summary of results by status
        
        Returns:
            Dictionary with counts by status
        """
        summary = {"PASS": 0, "FAIL": 0, "WARNING": 0, "INFO": 0, "ERROR": 0}

        for result in self.results:
            status = result.get("status", "UNKNOWN")
            if status in summary:
                summary[status] += 1

        return summary

    def get_summary_text(self) -> str:
        """
        Get summary text
        
        Returns:
            Summary as string
        """
        summary = self._get_summary()
        return (
            f"Results Summary:\n"
            f"  PASS: {summary['PASS']}\n"
            f"  FAIL: {summary['FAIL']}\n"
            f"  WARNING: {summary['WARNING']}\n"
            f"  INFO: {summary['INFO']}\n"
            f"  ERROR: {summary['ERROR']}\n"
            f"  Total: {len(self.results)}"
        )
