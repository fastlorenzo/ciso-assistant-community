"""Security module for CISO Assistant MCP Server"""

import json
from typing import Optional


def register_security_tools(mcp):
    """Register security tools with the MCP server"""
    
    # Import here to avoid circular imports
    from ..config import make_request, format_table

    @mcp.tool()
    async def get_security_measures(folder_id: Optional[str] = None):
        """Get security measures/controls

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("security-measures/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No security measures found"

        columns = ["name", "description", "type", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_security_incidents(folder_id: Optional[str] = None):
        """Get security incidents

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("security-incidents/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No security incidents found"

        columns = ["name", "description", "severity", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_security_exceptions(folder_id: Optional[str] = None):
        """Get security exceptions

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("security-exceptions/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No security exceptions found"

        columns = ["name", "description", "severity", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_vulnerabilities(folder_id: Optional[str] = None):
        """Get vulnerabilities

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("vulnerabilities/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No vulnerabilities found"

        columns = ["name", "description", "severity", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_findings(folder_id: Optional[str] = None):
        """Get findings from assessments

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("findings/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No findings found"

        columns = ["name", "description", "severity", "status", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_findings_assessments(folder_id: Optional[str] = None):
        """Get findings assessments

        Args:
            folder_id: Optional folder ID to filter results
        """
        params = {"folder": folder_id} if folder_id else {}
        result = make_request("findings-assessments/", params=params)

        if "error" in result:
            return f"Error: {result['error']}"

        if not result.get("results"):
            return "No findings assessments found"

        columns = ["name", "description", "status", "category", "folder"]
        return format_table(result["results"], columns)

    @mcp.tool()
    async def get_findings_severity_choices():
        """Get available severity choices for findings"""
        result = make_request("findings/severity/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_findings_status_choices():
        """Get available status choices for findings"""
        result = make_request("findings/status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_vulnerabilities_severity_choices():
        """Get available severity choices for vulnerabilities"""
        result = make_request("vulnerabilities/severity/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_vulnerabilities_status_choices():
        """Get available status choices for vulnerabilities"""
        result = make_request("vulnerabilities/status/")

        if "error" in result:
            return f"Error: {result['error']}"

        return json.dumps(result, indent=2)
