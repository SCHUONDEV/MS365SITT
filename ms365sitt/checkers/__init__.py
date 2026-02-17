"""Base checker class"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..client import GraphClient


class BaseChecker(ABC):
    """Base class for all security and compliance checkers"""

    def __init__(self, client: GraphClient):
        """
        Initialize checker
        
        Args:
            client: GraphClient instance
        """
        self.client = client
        self.results = []

    @abstractmethod
    def check(self) -> List[Dict[str, Any]]:
        """
        Run the compliance check
        
        Returns:
            List of check results
        """
        pass

    def add_result(
        self,
        check_name: str,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a check result
        
        Args:
            check_name: Name of the check
            status: Status (PASS, FAIL, WARNING, INFO)
            message: Description of the result
            details: Additional details
        """
        result = {
            "check": check_name,
            "status": status,
            "message": message,
            "details": details or {},
        }
        self.results.append(result)

    def get_results(self) -> List[Dict[str, Any]]:
        """Get all check results"""
        return self.results
